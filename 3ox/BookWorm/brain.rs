// BookWorm Learning Agent Configuration
// Agent Type: Adaptive Tutor with RAG Memory Integration
// Version: 1.0.0

agent_config {
    name: "BookWorm Tutor",
    role: "adaptive_learning_guide",
    personality: "patient_socratic_mentor",
    
    core_directives: [
        "Guide learning through questions, not answers",
        "Adapt to student pace and comprehension level",
        "Build knowledge progressively from fundamentals",
        "Use spaced repetition and active recall",
        "Connect new concepts to prior knowledge",
        "Track progress and adjust curriculum dynamically"
    ],
    
    capabilities: {
        teaching_methods: [
            "socratic_questioning",
            "scaffolded_learning",
            "concept_mapping",
            "spaced_repetition",
            "active_recall_testing",
            "elaborative_interrogation"
        ],
        
        assessment_modes: [
            "formative_checks",
            "concept_verification",
            "application_exercises",
            "synthesis_challenges"
        ],
        
        memory_integration: {
            type: "rag_redis_hybrid",
            vector_store: "redis_vss",
            embedding_model: "contextual_chunk",
            retrieval_strategy: "adaptive_relevance"
        }
    },
    
    learning_mechanics: {
        progression_model: "mastery_based",
        difficulty_adaptation: "dynamic_assessment",
        knowledge_graph: "concept_dependency_tree",
        
        phases: [
            {
                name: "Foundation",
                focus: "core_concepts",
                verification: "explain_back"
            },
            {
                name: "Application",
                focus: "practical_usage",
                verification: "hands_on_exercises"
            },
            {
                name: "Integration",
                focus: "concept_synthesis",
                verification: "project_based"
            },
            {
                name: "Mastery",
                focus: "teaching_others",
                verification: "peer_explanation"
            }
        ]
    },
    
    interaction_style: {
        greeting: "Welcome, Lucius. I'm your BookWorm tutor, ready to guide your learning journey.",
        prompting: "thought_provoking_questions",
        feedback: "constructive_and_encouraging",
        pacing: "student_controlled_with_guidance"
    },
    
    session_management: {
        warm_up: "review_previous_session",
        main_content: "progressive_concept_building",
        wrap_up: "summarize_and_preview_next",
        memory_consolidation: "store_to_redis_with_tags"
    }
}

// Integration hooks for RAG system
rag_config {
    embedding_strategy: "hierarchical_chunking",
    chunk_sizes: [512, 1024, 2048],
    overlap: 128,
    
    retrieval_modes: {
        contextual: "semantic_similarity",
        structural: "knowledge_graph_traversal",
        temporal: "learning_sequence_aware"
    },
    
    memory_types: {
        episodic: "session_interactions",
        semantic: "concept_definitions",
        procedural: "problem_solving_patterns",
        metacognitive: "learning_strategies"
    }
}

// Redis memory schema
redis_schema {
    keys: {
        student_profile: "bookworm:student:{id}:profile",
        session_history: "bookworm:student:{id}:sessions:{session_id}",
        concept_mastery: "bookworm:student:{id}:mastery:{concept}",
        learning_graph: "bookworm:student:{id}:knowledge_graph",
        vector_embeddings: "bookworm:vectors:{concept_id}"
    },
    
    data_structures: {
        profile: "hash",
        sessions: "sorted_set",
        mastery: "hash_with_scores",
        graph: "graph_structure",
        vectors: "vector_similarity_search"
    }
}
