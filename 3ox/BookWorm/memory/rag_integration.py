"""
RAG (Retrieval-Augmented Generation) Integration for BookWorm
Connects learning content with Redis Vector Store for semantic search
"""

import json
import hashlib
from typing import List, Dict, Optional, Tuple
import numpy as np


class RAGMemorySystem:
    """
    Integrates with Redis for vector storage and retrieval
    Enables semantic search across learning materials and past sessions
    """
    
    def __init__(self, redis_client, embedding_function=None):
        """
        Initialize RAG system
        
        Args:
            redis_client: Redis connection with VSS (Vector Similarity Search)
            embedding_function: Function to generate embeddings (defaults to simple hash)
        """
        self.redis = redis_client
        self.embed = embedding_function or self._simple_embedding
        self.chunk_size = 512
        self.overlap = 128
    
    def ingest_book(self, book_path: str, book_metadata: Dict):
        """
        Ingest a book into the RAG system
        Chunks content, generates embeddings, stores in Redis VSS
        """
        with open(book_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Hierarchical chunking
        chunks = self._create_hierarchical_chunks(content)
        
        # Process each chunk
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{book_metadata['id']}:chunk:{idx}"
            
            # Generate embedding
            embedding = self.embed(chunk['text'])
            
            # Store in Redis
            self._store_chunk(
                chunk_id=chunk_id,
                text=chunk['text'],
                embedding=embedding,
                metadata={
                    **book_metadata,
                    'chunk_index': idx,
                    'chunk_type': chunk['type'],
                    'section': chunk.get('section', ''),
                    'concepts': chunk.get('concepts', [])
                }
            )
        
        return len(chunks)
    
    def _create_hierarchical_chunks(self, content: str) -> List[Dict]:
        """
        Create hierarchical chunks from content
        Maintains structure: sections > paragraphs > sentences
        """
        chunks = []
        
        # Split by major sections (## headers in markdown)
        sections = content.split('\n## ')
        
        for section_idx, section in enumerate(sections):
            lines = section.split('\n')
            section_title = lines[0] if lines else ''
            section_content = '\n'.join(lines[1:]) if len(lines) > 1 else ''
            
            # Create section-level chunk
            if len(section_content) > self.chunk_size:
                # Further split into paragraph chunks
                paragraphs = section_content.split('\n\n')
                current_chunk = []
                current_size = 0
                
                for para in paragraphs:
                    para_size = len(para)
                    
                    if current_size + para_size > self.chunk_size and current_chunk:
                        # Save current chunk
                        chunks.append({
                            'type': 'paragraph_group',
                            'text': '\n\n'.join(current_chunk),
                            'section': section_title,
                            'concepts': self._extract_concepts('\n\n'.join(current_chunk))
                        })
                        
                        # Start new chunk with overlap
                        if len(current_chunk) > 1:
                            current_chunk = current_chunk[-1:]
                            current_size = len(current_chunk[0])
                        else:
                            current_chunk = []
                            current_size = 0
                    
                    current_chunk.append(para)
                    current_size += para_size
                
                # Save remaining
                if current_chunk:
                    chunks.append({
                        'type': 'paragraph_group',
                        'text': '\n\n'.join(current_chunk),
                        'section': section_title,
                        'concepts': self._extract_concepts('\n\n'.join(current_chunk))
                    })
            else:
                # Section fits in one chunk
                chunks.append({
                    'type': 'section',
                    'text': section_content,
                    'section': section_title,
                    'concepts': self._extract_concepts(section_content)
                })
        
        return chunks
    
    def _extract_concepts(self, text: str) -> List[str]:
        """
        Extract key concepts from text
        In production, use NLP/LLM for better extraction
        """
        # Simple keyword extraction (placeholder)
        words = text.lower().split()
        
        # Filter for potential concept words (longer, capitalized in original)
        concepts = []
        for word in words:
            if len(word) > 6 and word.isalpha():
                concepts.append(word)
        
        return list(set(concepts))[:10]  # Top 10 unique concepts
    
    def _simple_embedding(self, text: str) -> List[float]:
        """
        Simple embedding using hash-based features
        In production, use proper embedding model (OpenAI, sentence-transformers, etc.)
        """
        # Generate consistent hash-based embedding (768 dimensions)
        hash_obj = hashlib.sha512(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float array
        embedding = []
        for i in range(0, len(hash_bytes), 8):
            chunk = hash_bytes[i:i+8]
            value = int.from_bytes(chunk, 'big') / (2**64)
            embedding.append(value)
        
        # Normalize
        embedding = np.array(embedding[:768])  # Truncate to 768 dims
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.tolist()
    
    def _store_chunk(self, chunk_id: str, text: str, embedding: List[float], metadata: Dict):
        """Store chunk in Redis with vector embedding"""
        if not self.redis:
            return
        
        # Store text and metadata in hash
        key = f"bookworm:chunks:{chunk_id}"
        self.redis.hset(key, mapping={
            'text': text,
            'metadata': json.dumps(metadata)
        })
        
        # Store vector embedding (using sorted set as placeholder)
        # In production Redis VSS, use: redis.ft().add_document()
        vector_key = f"bookworm:vectors:{chunk_id}"
        self.redis.hset(vector_key, mapping={
            'vector': json.dumps(embedding),
            'chunk_id': chunk_id
        })
    
    def semantic_search(self, query: str, top_k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Perform semantic search across stored content
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters (book_id, concepts, etc.)
        
        Returns:
            List of relevant chunks with scores
        """
        # Generate query embedding
        query_embedding = self.embed(query)
        
        # Search in Redis VSS
        results = self._vector_search(query_embedding, top_k, filters)
        
        return results
    
    def _vector_search(self, query_embedding: List[float], top_k: int, filters: Optional[Dict]) -> List[Dict]:
        """
        Perform vector similarity search
        In production, use Redis VSS native search
        """
        if not self.redis:
            return []
        
        # Get all vector keys (in production, use Redis VSS index)
        vector_keys = []
        cursor = 0
        while True:
            cursor, keys = self.redis.scan(cursor, match="bookworm:vectors:*", count=100)
            vector_keys.extend(keys)
            if cursor == 0:
                break
        
        # Calculate similarities
        similarities = []
        query_vec = np.array(query_embedding)
        
        for key in vector_keys[:100]:  # Limit for demo
            stored = self.redis.hgetall(key)
            if not stored or 'vector' not in stored:
                continue
            
            stored_vec = np.array(json.loads(stored['vector']))
            
            # Cosine similarity
            similarity = np.dot(query_vec, stored_vec)
            
            chunk_id = stored['chunk_id']
            similarities.append((similarity, chunk_id))
        
        # Sort and get top-k
        similarities.sort(reverse=True)
        top_results = similarities[:top_k]
        
        # Fetch full chunk data
        results = []
        for score, chunk_id in top_results:
            chunk_key = f"bookworm:chunks:{chunk_id}"
            chunk_data = self.redis.hgetall(chunk_key)
            
            if chunk_data:
                results.append({
                    'chunk_id': chunk_id,
                    'text': chunk_data.get('text', ''),
                    'metadata': json.loads(chunk_data.get('metadata', '{}')),
                    'similarity_score': float(score)
                })
        
        return results
    
    def retrieve_context_for_concept(self, concept_id: str, student_id: str) -> Dict:
        """
        Retrieve relevant context for teaching a concept
        Combines:
        - Concept definition from knowledge base
        - Related past student interactions
        - Relevant book sections
        """
        # Search for concept in knowledge base
        concept_results = self.semantic_search(
            query=concept_id,
            top_k=3,
            filters={'type': 'concept_definition'}
        )
        
        # Retrieve student's past interactions with this concept
        student_history = self._get_student_concept_history(student_id, concept_id)
        
        # Find related examples and explanations
        examples = self.semantic_search(
            query=f"examples of {concept_id}",
            top_k=2,
            filters={'type': 'example'}
        )
        
        return {
            'definitions': concept_results,
            'student_history': student_history,
            'examples': examples,
            'context_summary': self._create_context_summary(concept_results, examples)
        }
    
    def _get_student_concept_history(self, student_id: str, concept_id: str) -> List[Dict]:
        """Retrieve student's past interactions with concept from Redis"""
        if not self.redis:
            return []
        
        key = f"bookworm:student:{student_id}:concept_history:{concept_id}"
        history_data = self.redis.lrange(key, 0, -1)
        
        return [json.loads(item) for item in history_data]
    
    def _create_context_summary(self, definitions: List[Dict], examples: List[Dict]) -> str:
        """Create a consolidated context summary for the tutor"""
        summary = "## Context for Teaching\n\n"
        
        if definitions:
            summary += "**Key Definitions:**\n"
            for def_item in definitions[:2]:
                summary += f"- {def_item['text'][:200]}...\n"
        
        if examples:
            summary += "\n**Examples to Use:**\n"
            for ex_item in examples:
                summary += f"- {ex_item['text'][:200]}...\n"
        
        return summary
    
    def store_interaction(self, student_id: str, concept_id: str, interaction: Dict):
        """Store student interaction for future retrieval"""
        if not self.redis:
            return
        
        key = f"bookworm:student:{student_id}:concept_history:{concept_id}"
        interaction_data = json.dumps({
            **interaction,
            'timestamp': interaction.get('timestamp', 0)
        })
        
        # Store in list (most recent first)
        self.redis.lpush(key, interaction_data)
        
        # Keep only last 50 interactions
        self.redis.ltrim(key, 0, 49)
    
    def get_spaced_repetition_items(self, student_id: str) -> List[Dict]:
        """
        Retrieve concepts due for review based on spaced repetition algorithm
        Uses forgetting curve and last review timestamp
        """
        if not self.redis:
            return []
        
        # Get all concept mastery records
        pattern = f"bookworm:student:{student_id}:mastery:*"
        cursor = 0
        due_items = []
        
        while True:
            cursor, keys = self.redis.scan(cursor, match=pattern, count=100)
            
            for key in keys:
                mastery_data = self.redis.hgetall(key)
                if not mastery_data:
                    continue
                
                concept_id = key.split(':')[-1]
                last_updated = float(mastery_data.get('last_updated', 0))
                level = int(mastery_data.get('level', 0))
                
                # Calculate review interval (exponential backoff)
                intervals = [1, 3, 7, 14, 30]  # days
                interval_days = intervals[min(level, len(intervals)-1)]
                
                # Check if due
                import time
                days_since = (time.time() - last_updated) / 86400
                
                if days_since >= interval_days:
                    due_items.append({
                        'concept_id': concept_id,
                        'level': level,
                        'days_overdue': days_since - interval_days,
                        'priority': (days_since - interval_days) * (5 - level)  # Higher priority for overdue + lower mastery
                    })
            
            if cursor == 0:
                break
        
        # Sort by priority
        due_items.sort(key=lambda x: x['priority'], reverse=True)
        
        return due_items[:10]  # Return top 10 due items
