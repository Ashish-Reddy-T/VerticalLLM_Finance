import faiss, pickle, os, re
from sentence_transformers import SentenceTransformer, CrossEncoder
from pathlib import Path
from llama_cpp import Llama

path = str(Path(__file__).parent)
faiss_path = os.path.join(path, "data", "rag_index.faiss")
pkl_path = os.path.join(path, "data", "rag_index_chunks.pkl")
txt_path = os.path.join(path, "data", "rag_index_model_name.txt")

def load_index():
    return faiss.read_index(faiss_path)

def load_chunks():
    with open(pkl_path, "rb") as f:
        return pickle.load(f)

def load_embedding_model():
    with open(txt_path, 'r') as f:
        model_name = f.read().strip()
    model = SentenceTransformer(model_name)
    return model

def load_cross_encoding_model():
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return reranker

class SelfRAG:
    def __init__(self, llm: Llama, top_k=20, top_n=6, threshold=0.25):
        self.top_k = top_k
        self.top_n = top_n
        self.retrieval_threshold = threshold
        self.llm = llm

        self.index = load_index()
        self.chunks = load_chunks()
        self.embedding_model = load_embedding_model()
        self.reranker = load_cross_encoding_model()

        self.special_tokens = {
            "retrieve": "[Retrieve]",
            "relevant": "[Relevant]",
            "irrelevant": "[Irrelevant]",
            "supported": "[Supported]",
            "not_supported": "[Not Supported]",
            "partial": "[Partially Supported]"
        }

    def should_retrieve(self, query: str) -> bool:
        # Fast search: Simple semantic patterns
        if re.search(r'(meaning|concept|theory|hypothesis) of', query, re.IGNORECASE):
            return True
        
        # Slow search: LLM use
        return self._llm_retrieve_decision(query)
    
    def _llm_retrieve_decision(self, query: str) -> bool:
        prompt = f"""
[INST] Should we retrieve documents for this query? 

Consider: Is it about financial concepts/definitions/theories/advices/recommendations/suggestions?
Answer ONLY 'yes' or 'no'.

Query: "{query}"
Answer: [/INST]"""
        
        response = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1,
            temperature=0.0
        )

        # Debugging
        print("INFO: RETRIEVE0 (yes/no):", response['choices'][0]['message']['content'].strip().lower())
        return "yes" in response['choices'][0]['message']['content'].strip().lower()

    
    
    def retrieve(self, query: str) -> list:
        query_emb = self.embedding_model.encode([query], convert_to_numpy=True)
        scores, indices = self.index.search(query_emb, self.top_k)
        return [self.chunks[i] for i in indices[0]]

    def rerank(self, query, retrieved_chunks):
        pairs = [(query, chunk) for chunk in retrieved_chunks]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(retrieved_chunks, scores), key=lambda x: x[1], reverse=True)
        top_chunks = [text for text, score in ranked[:self.top_n]]
        return top_chunks
    
    def critique_passage(self, query: str, passage: str) -> str:
        """Enhanced critique with multi-level evaluation"""
        # First check basic relevance
        relevance_prompt = f"""
[INST] Determine if this passage is relevant to the query. 

Query: '{query}'
Passage: '{passage[:1000]}...'

Answer only 'relevant', 'irrelevant', or 'partial': [/INST]"""
        
        relevance_response = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": relevance_prompt}],
            max_tokens=4,
            temperature=0.0
        )
        relevance = relevance_response['choices'][0]['message']['content'].strip().lower()

        # Debugging
        print("INFO: RETRIEVE1 (relevant/irrelevant/partial):", relevance)
        
        if 'irrelevant' in relevance:
            return self.special_tokens["irrelevant"]
        
        # For relevant passages, check factual support
        support_prompt = f"""
[INST] Verify if the passage provides accurate information that directly supports answering the query. 

Query: '{query}'
Passage: '{passage[:800]}...'

Answer only 'supported', 'not supported', or 'partial': [/INST]"""
        
        support_response = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": support_prompt}],
            max_tokens=4,
            temperature=0.0
        )
        support = support_response['choices'][0]['message']['content'].strip().lower()

        # Debugging
        print("INFO: RETRIEVE2 (supported/not supported/partial):", relevance)
        
        if 'supported' in support:
            return self.special_tokens["supported"]
        elif 'not supported' in support or 'not_supported' in support:
            return self.special_tokens["not_supported"]
        return self.special_tokens["partial"]
    
    def generate_with_rag(self, query: str) -> str:
        """Core Self-RAG generation with enhanced context handling"""
        if not self.should_retrieve(query):
            return self._direct_generate(query)
        
        retrieved = self.retrieve(query)
        passages = self.rerank(query, retrieved)
        
        context = "Relevant knowledge from documents:\n\n"
        for passage in passages:
            critique = self.critique_passage(query, passage)
            
            if critique == self.special_tokens["supported"]:
                confidence = 1.0
            elif critique == self.special_tokens["partial"]:
                confidence = 0.5
            elif critique == self.special_tokens["not_supported"]:
                confidence = 0.3
            elif critique == self.special_tokens["irrelevant"]:
                confidence = 0.1
                
            context += f"{critique} (Confidence: {confidence:.1f}): {passage}\n\n"
        
        return self._generate_with_context(query, context)
    
    def _generate_with_context(self, query: str, context: str) -> str:
        """Generate with RAG context and critique guidance"""
        prompt = f"""
[INST] You are a financial expert answering questions. Use the provided context to answer the query, paying attention to the critique tokens:

- [Relevant]: Information is directly relevant
- [Irrelevant]: Can be ignored
- [Supported]: Information is accurate and supported
- [Not Supported]: Information is contradicted by evidence
- [Partially Supported]: Information is partially accurate

Context:
{context}

Question: {query}

Structure your response:
- Address the question directly
- Reference relevant context with critique tokens
- Explain any contradictions or limitations
- Provide a comprehensive answer
[/INST]"""
        
        response = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.7
        )

        return response['choices'][0]['message']['content']
    
    def _direct_generate(self, query: str) -> str:
        """Generate without retrieval"""
        prompt = f"[INST] {query} [/INST]"
        response = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256
        )
        print("\nAgent: No Self-RAG required. Using LLM knowledge to answer.")
        return response['choices'][0]['message']['content']