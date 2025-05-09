import uuid
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointIdsList,
    PointStruct,
    Range,
    VectorParams,
    SearchRequest,
    MatchAny, 
    ScoredPoint,
    CollectionsResponse,
    CollectionInfo
)

class AsyncQdrant():
    def __init__(
        self,
        collection_name: str,
        embedding_model_dims: int,
        url: str,
    ):
        """
        Initialize the Qdrant vector store.

        Args:
            collection_name (str): Name of the collection.
            embedding_model_dims (int): Dimensions of the embedding model.
            url (str, optional): Full URL for Qdrant server. Defaults to None.
        """
        self.client = AsyncQdrantClient(url=url)

        self.collection_name = collection_name
        self.embedding_model_dims = embedding_model_dims

        self.score_threshold = 0.7
        self.output_num_limit = 3

    async def create_collections_if_not_exist(self, distance: Distance = Distance.COSINE):
        """
        Create a new collection.

        Args:
            vector_size (int): Size of the vectors to be stored.
            on_disk (bool): Enables persistent storage.
            distance (Distance, optional): Distance metric for vector similarity. Defaults to Distance.COSINE.
        """
        # Skip creating collection if already exists
        response = await self.list_cols()
        for collection in response.collections:
            if collection.name == self.collection_name:
                return

        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.embedding_model_dims, distance=distance),
        )

    async def insert(self, vectors: list, payloads: list = None, ids: list = None) -> list[str]:
        """
        Insert vectors into a collection.

        Args:
            vectors (list): List of vectors to insert.
            payloads (list, optional): List of payloads corresponding to vectors. Defaults to None.
            ids (list, optional): List of IDs corresponding to vectors. Defaults to None.
        """
        generated_ids = [str(uuid.uuid4()) for _ in vectors] if ids is None else [str(i) for i in ids]
        points = [
            PointStruct(
                id=generated_ids[idx],
                vector=vector,
                payload=payloads[idx] if payloads else {},
            )
            for idx, vector in enumerate(vectors)
        ]
        
        await self.client.upsert(collection_name=self.collection_name, points=points)
        return generated_ids


    def _create_filter(self, filters: dict) -> Filter:
        """
        Create a Filter object from the provided filters.

        Args:
            filters (dict): Filters to apply. Supports:
                - exact match: {"user_id": "abc"}
                - list match: {"language": {"in": ["en", "vi"]}}
                - range: {"score": {"gte": 0.5, "lte": 1.0}}

        Returns:
            Filter: The created Filter object.
        """
        conditions = []

        for key, value in filters.items():
            if isinstance(value, dict):
                if "gte" in value and "lte" in value:
                    conditions.append(
                        FieldCondition(key=key, range=Range(gte=value["gte"], lte=value["lte"]))
                    )
                elif "in" in value and isinstance(value["in"], list):
                    conditions.append(
                        FieldCondition(key=key, match=MatchAny(any=value["in"]))
                    )
                else:
                    raise ValueError(f"Unsupported filter format for key '{key}': {value}")
            else:
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )

        return Filter(must=conditions) if conditions else None

    # async def search_1d(self, query: list[float], limit: int = None, filters: dict = None, score_threshold: float = None) -> list[ScoredPoint]:
    #     """
    #     Search for similar vectors.

    #     Args:
    #         query (list): word vector.
    #         limit (int, optional): Number of results to return. Defaults to 5.
    #         filters (dict, optional): Filters to apply to the search. Defaults to None.

    #     Returns:
    #         list: [related_phrases_num] each element is a Scorepoint
    #     """
    #     if limit == None: 
    #         limit = self.output_num_limit
    #     if score_threshold == None:
    #         score_threshold = self.score_threshold

    #     query_filter = self._create_filter(filters) if filters else None
    #     hits = await self.client.search(
    #         collection_name=self.collection_name,
    #         query_vector=query,
    #         query_filter=query_filter,
    #         limit=limit,
    #         with_payload=True,
    #         with_vectors=False,
    #         score_threshold=score_threshold,
    #     )
    #     return hits 
    
    # async def search_2d(self, query: list[list[float]], limit: int = None, filters: dict = None, score_threshold: float = None) -> list[list[ScoredPoint]]:
    #     """
    #     Search for similar vectors.

    #     Args:
    #         query (list[list[float]]): [words_num], each element is a word vector
    #         limit (int, optional): Number of results to return. Defaults to 5.
    #         filters (dict, optional): Filters to apply to the search. Defaults to None.

    #     Returns:
    #         list[list]: [words_num, related_phrases_num] each element is a Scorepoint
    #     """
    #     if limit == None: 
    #         limit = self.output_num_limit
    #     if score_threshold == None:
    #         score_threshold = self.score_threshold

    #     query_filter = self._create_filter(filters) if filters else None

    #     #[num_words, num_related_words]
    #     hits_batch = await self.client.search_batch(
    #         collection_name=self.collection_name,
    #         requests=[SearchRequest(
    #             vector=word_vector,
    #             limit=limit,
    #             filter=query_filter,
    #             with_payload=True,
    #             with_vector=False,
    #             score_threshold=score_threshold,
    #         ) for word_vector in query]
    #     )

    #     return hits_batch

    async def search_3d(self, word_embedding_2d: list[list[list[float]]], word_data_2d: list[list[dict]], limit: int = None, filters: dict = None, score_threshold: float = None)-> list[list[list[ScoredPoint]]]:
        """
        Search for similar vectors.

        Args:
            word_embedding_2 (list[list[list[float]]]): [sentence][word][vector]
            word_data_2d (list[list[dict]]): [sentence][word], an element is a list of dict
            limit (int, optional): Number of results to return per query. Defaults to 10.
            filters (dict, optional): Filters to apply to the search. Defaults to None.
            score_threshold (float, optional): Minimum similarity score threshold. Defaults to 0.7.

        Returns:
            list[list[list]]: [num_sentences, num_words, num_related_phrases], each element is a ScorePoint
        """
        if limit == None: 
            limit = self.output_num_limit
        if score_threshold == None:
            score_threshold = self.score_threshold
            
        query_filter = self._create_filter(filters) if filters else None

        # Step 1: Collect all SearchRequests with their positions
        search_requests = []
        positions = []  # to remember where to put results later    

        for sent_idx, (word_embedding_1d, word_data_1d) in enumerate(zip(word_embedding_2d, word_data_2d)):
            for word_idx, (word_embedding, word_data) in enumerate(zip(word_embedding_1d, word_data_1d)):
                if not word_data.get('ignore', False):
                    search_request = SearchRequest(
                        vector=word_embedding,
                        limit=limit,
                        filter=query_filter,
                        with_payload=True,
                        with_vector=False,
                        score_threshold=score_threshold,
                    )
                    search_requests.append(search_request)
                    positions.append((sent_idx, word_idx))

        # Step 2: Async batch search
        batch_results = await self.client.search_batch(
            collection_name=self.collection_name,
            requests=search_requests,
        )
        
        # Step 3: Initialize empty 3D result list
        result = [
            [[] for _ in sentence]
            for sentence in word_data_2d
        ]

        # Step 4: Fill in the results
        for (sent_idx, word_idx), scored_points in zip(positions, batch_results):
            result[sent_idx][word_idx] = scored_points

        return result
    
    async def check_exist(self, filters: dict):
        query_filter = self._create_filter(filters) if filters else None
        hits = await self.client.scroll(collection_name=self.collection_name ,scroll_filter=query_filter, limit=1)
        return hits

    async def delete(self, id: str) -> None:
        """
        Delete a vector by ID.

        Args:
            vector_id (str): ID of the vector to delete.
        """
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(
                points=[id],
            ),
        )
    
    async def delete_1d(self, id_1d: list[str]) -> None:
        """
        Delete vectors by ID.

        Args:
            id_1d (list[str]): list of ID of vectors to delete.
        """
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(
                points=id_1d,
            ),
        )

    async def update(self, vector_id: str, vector: list = None, payload: dict = None) -> None:
        """
        Update a vector and its payload.

        Args:
            vector_id (str): ID of the vector to update.
            vector (list, optional): Updated vector. Defaults to None.
            payload (dict, optional): Updated payload. Defaults to None.
        """
        point = PointStruct(id=vector_id, vector=vector, payload=payload)
        await self.client.upsert(collection_name=self.collection_name, points=[point])

    async def get(self, vector_id: str):
        """
        Retrieve a vector by ID.

        Args:
            vector_id (str): ID of the vector to retrieve.

        Returns:
            dict: Retrieved vector.
        """
        result = await self.client.retrieve(collection_name=self.collection_name, ids=[vector_id], with_payload=True)
        return result[0] if result else None

    async def list_cols(self) -> CollectionsResponse:
        """
        List all collections.

        Returns:
            list: List of collection names.
        """
        result = await self.client.get_collections()
        return result

    async def delete_col(self) -> None:
        """Delete a collection."""
        await self.client.delete_collection(collection_name=self.collection_name)

    async def col_info(self) -> CollectionInfo:
        """
        Get information about a collection.

        Returns:
            dict: Collection information.
        """
        result = await self.client.get_collection(collection_name=self.collection_name)
        return result

    async def list(self, filters: dict = None, limit: int = 1000):
        """
        List all vectors in a collection.

        Args:
            filters (dict, optional): Filters to apply to the list. Defaults to None.
            limit (int, optional): Number of vectors to return. Defaults to 100.

        Returns:
            list: List of vectors.
        """
        query_filter = self._create_filter(filters) if filters else None
        result = await self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=query_filter,
            limit = limit,
            with_payload=True,
            with_vectors=False,
        )
        return result[0]