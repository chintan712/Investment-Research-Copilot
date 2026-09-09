CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
	id SERIAL PRIMARY KEY,
	filename VARCHAR(255) NOT NULL,
	document_type VARCHAR(80),
	uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
	id SERIAL PRIMARY KEY,
	document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
	page_number INTEGER NOT NULL,
	chunk_index INTEGER NOT NULL,
	content TEXT NOT NULL,
	embedding vector(1536) NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_requests (
	id SERIAL PRIMARY KEY,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	question TEXT NOT NULL,
	model VARCHAR(120),
	input_tokens INTEGER,
	output_tokens INTEGER,
	total_tokens INTEGER,
	retrieved_chunks INTEGER DEFAULT 0,
	latency_ms INTEGER DEFAULT 0,
	response TEXT NOT NULL,
	metadata_json JSON DEFAULT '{}'::json
);
