export type DocumentListResponse = { files: string[]; file_count: number; };
export type DocumentIndexResponse = { status: string; indexed_files: string[]; indexed_file_count: number; message: string; };
export type UploadResponse = { filename: string; saved_as: string; content_type: string | null; size_bytes: number; status: string; };
