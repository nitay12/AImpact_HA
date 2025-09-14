"""
RAG System with FAISS vector store and multilingual embeddings.
Supports Hebrew regulatory text retrieval and semantic search.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import faiss
from sentence_transformers import SentenceTransformer
from data_processor import RegulatoryDataProcessor, RegulationChunk


class RegulatoryRAGSystem:
    """RAG system for regulatory requirements with Hebrew support."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        index_file: str = "regulatory_index.faiss",
        chunks_file: str = "regulatory_chunks.pkl"
    ):
        self.model_name = model_name
        self.index_file = index_file
        self.chunks_file = chunks_file

        # Initialize components
        self.encoder = None
        self.index = None
        self.chunks: List[RegulationChunk] = []
        self.dimension = None

        # Load or initialize
        self._initialize_encoder()

    def _initialize_encoder(self):
        """Initialize the sentence transformer model."""
        print(f"Loading embedding model: {self.model_name}")
        self.encoder = SentenceTransformer(self.model_name)
        self.dimension = self.encoder.get_sentence_embedding_dimension()
        print(f"Embedding dimension: {self.dimension}")

    def build_index(self, json_file_path: str):
        """Build FAISS index from regulatory JSON data."""
        print("Processing regulatory data...")

        # Process data
        processor = RegulatoryDataProcessor(json_file_path)
        processor.load_data()
        self.chunks = processor.create_chunks()

        print(f"Created {len(self.chunks)} regulatory chunks")

        # Generate embeddings
        print("Generating embeddings...")
        texts = [chunk.content for chunk in self.chunks]
        embeddings = self.encoder.encode(texts, show_progress_bar=True)

        # Build FAISS index
        print("Building FAISS index...")
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings.astype(np.float32))
        self.index.add(embeddings.astype(np.float32))

        # Save index and chunks
        self.save_index()
        print(f"Built index with {self.index.ntotal} vectors")

    def save_index(self):
        """Save FAISS index and chunks to disk."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_file)
            print(f"Saved FAISS index to {self.index_file}")

        if self.chunks:
            with open(self.chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            print(f"Saved chunks to {self.chunks_file}")

    def load_index(self):
        """Load FAISS index and chunks from disk."""
        if os.path.exists(self.index_file) and os.path.exists(self.chunks_file):
            self.index = faiss.read_index(self.index_file)

            with open(self.chunks_file, 'rb') as f:
                self.chunks = pickle.load(f)

            print(f"Loaded index with {self.index.ntotal} vectors and {len(self.chunks)} chunks")
            return True
        return False

    def search(
        self,
        query: str,
        k: int = 5,
        business_profile: Optional[Dict[str, Any]] = None,
        category_filter: Optional[str] = None
    ) -> List[Tuple[RegulationChunk, float]]:
        """
        Search for relevant regulations.

        Args:
            query: Search query in Hebrew or English
            k: Number of results to return
            business_profile: Business characteristics for compliance filtering
            category_filter: Filter by regulation category

        Returns:
            List of (chunk, score) tuples
        """
        if self.index is None or not self.chunks:
            raise ValueError("Index not built or loaded")

        # Encode query
        query_embedding = self.encoder.encode([query])
        faiss.normalize_L2(query_embedding.astype(np.float32))

        # Search in FAISS
        scores, indices = self.index.search(query_embedding.astype(np.float32), k * 2)  # Get more for filtering

        # Prepare results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx]

                # Apply filters
                if category_filter and chunk.category != category_filter:
                    continue

                if business_profile:
                    processor = RegulatoryDataProcessor("")
                    processor.chunks = self.chunks  # Set chunks for compliance check
                    if not processor.check_business_compliance(business_profile, chunk):
                        continue

                results.append((chunk, float(score)))

                if len(results) >= k:
                    break

        return results

    def hybrid_search(
        self,
        query: str,
        business_profile: Dict[str, Any],
        k: int = 5,
        semantic_weight: float = 0.7,
        compliance_weight: float = 0.3
    ) -> List[Tuple[RegulationChunk, float]]:
        """
        Hybrid search combining semantic similarity and compliance relevance.

        Args:
            query: Search query
            business_profile: Business characteristics
            k: Number of results
            semantic_weight: Weight for semantic similarity
            compliance_weight: Weight for compliance relevance

        Returns:
            List of (chunk, score) tuples with combined scoring
        """
        if self.index is None or not self.chunks:
            raise ValueError("Index not built or loaded")

        # Get semantic results
        semantic_results = self.search(query, k * 3, business_profile=None)

        # Create processor for compliance checking
        processor = RegulatoryDataProcessor("")
        processor.chunks = self.chunks

        # Re-score results with hybrid approach
        hybrid_results = []
        for chunk, semantic_score in semantic_results:
            # Calculate compliance score
            compliance_score = 1.0 if processor.check_business_compliance(business_profile, chunk) else 0.1

            # Calculate attribute relevance (how well business matches conditions)
            attr_relevance = self._calculate_attribute_relevance(chunk, business_profile)

            # Combined score
            final_score = (
                semantic_weight * semantic_score +
                compliance_weight * compliance_score +
                0.1 * attr_relevance  # Small boost for attribute alignment
            )

            hybrid_results.append((chunk, final_score))

        # Sort by final score and return top k
        hybrid_results.sort(key=lambda x: x[1], reverse=True)
        return hybrid_results[:k]

    def _calculate_attribute_relevance(self, chunk: RegulationChunk, business_profile: Dict[str, Any]) -> float:
        """Calculate how well business attributes align with regulation conditions."""
        if not chunk.conditions:
            return 0.5  # Neutral score for regulations without conditions

        relevance_scores = []

        for condition in chunk.conditions:
            if "logic" in condition and condition["logic"] == "OR":
                # OR conditions - check all clauses
                clause_scores = []
                for clause in condition["clauses"]:
                    clause_score = self._score_single_condition(clause, business_profile)
                    clause_scores.append(clause_score)
                relevance_scores.append(max(clause_scores))  # Best clause score
            else:
                # Regular condition
                score = self._score_single_condition(condition, business_profile)
                relevance_scores.append(score)

        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

    def _score_single_condition(self, condition: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """Score how well a single condition matches the business profile."""
        attribute = condition.get("attribute")
        operator = condition.get("operator")
        threshold = condition.get("value")

        if attribute not in profile:
            return 0.0

        business_value = profile[attribute]

        # Calculate proximity score based on how close business value is to threshold
        if operator == "less_than_or_equal_to":
            if business_value <= threshold:
                return 1.0  # Perfect match
            else:
                # Penalty for exceeding threshold
                return max(0.0, 1.0 - (business_value - threshold) / threshold * 0.5)

        elif operator == "greater_than":
            if business_value > threshold:
                return 1.0  # Perfect match
            else:
                # Penalty for being below threshold
                return max(0.0, business_value / threshold * 0.8)

        elif operator == "greater_than_or_equal_to":
            if business_value >= threshold:
                return 1.0  # Perfect match
            else:
                return max(0.0, business_value / threshold * 0.8)

        elif operator == "equal_to":
            if business_value == threshold:
                return 1.0
            else:
                return 0.0

        return 0.0

    def get_regulation_summary(self, chunks: List[RegulationChunk]) -> Dict[str, Any]:
        """Generate a summary of retrieved regulations."""
        if not chunks:
            return {"total": 0, "categories": {}, "authorities": {}}

        categories = {}
        authorities = {}

        for chunk in chunks:
            # Count by category
            if chunk.category in categories:
                categories[chunk.category] += 1
            else:
                categories[chunk.category] = 1

            # Count by authority
            if chunk.source_authority in authorities:
                authorities[chunk.source_authority] += 1
            else:
                authorities[chunk.source_authority] = 1

        return {
            "total": len(chunks),
            "categories": categories,
            "authorities": authorities
        }


def main():
    """Test the RAG system."""
    rag = RegulatoryRAGSystem()

    # Build index
    print("Building index...")
    rag.build_index("data.json")

    # Test search
    print("\nTesting search...")
    query = "דרישות בטיחות אש למקום ישיבה"
    business_profile = {
        "seating_capacity": 75,
        "size_sqm": 100
    }

    results = rag.hybrid_search(query, business_profile, k=3)

    print(f"\nFound {len(results)} results for query: '{query}'")
    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n{i}. {chunk.requirement_name} (Score: {score:.3f})")
        print(f"   Category: {chunk.category}")
        print(f"   Source: {chunk.doc_source}")
        print(f"   Text: {chunk.raw_text[:100]}...")


if __name__ == "__main__":
    main()