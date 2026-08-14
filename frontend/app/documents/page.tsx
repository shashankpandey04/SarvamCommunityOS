"use client";

import {
  ChangeEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  getDocuments,
  uploadDocument,
} from "@/lib/api";

import type {
  Document,
} from "@/types/api";


export default function DocumentsPage() {

  const fileInputRef = useRef<HTMLInputElement>(
    null
  );

  const [
    documents,
    setDocuments,
  ] = useState<Document[]>([]);

  const [
    uploading,
    setUploading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );

  const [
    success,
    setSuccess,
  ] = useState<string | null>(
    null
  );


  // =====================================================
  // Load Documents
  // =====================================================

  async function loadDocuments() {

    try {

      setError(null);

      const data = await getDocuments();

      setDocuments(data);

    } catch (error) {

      setError(
        error instanceof Error
          ? error.message
          : "Failed to load documents."
      );
    }
  }


  // =====================================================
  // Initial Load
  // =====================================================

  useEffect(() => {

    loadDocuments();

  }, []);


  // =====================================================
  // Upload
  // =====================================================

  async function handleUpload(
    event: ChangeEvent<HTMLInputElement>,
  ) {

    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (
      file.type !== "application/pdf"
    ) {

      setError(
        "Please select a PDF file."
      );

      return;
    }

    try {

      setUploading(true);

      setError(null);
      setSuccess(null);

      const result =
        await uploadDocument(file);

      setSuccess(
        `Processed ${result.filename} and created ${result.sections} knowledge sections.`
      );

      await loadDocuments();

    } catch (error) {

      setError(
        error instanceof Error
          ? error.message
          : "Failed to upload document."
      );

    } finally {

      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }


  return (
    <div className="space-y-8">

      {/* ================================================= */}
      {/* Header */}
      {/* ================================================= */}

      <div className="flex items-start justify-between">

        <div>

          <h1 className="text-2xl font-semibold">
            Documents
          </h1>

          <p className="mt-1 text-sm text-zinc-500">
            Upload documentation to expand
            CommunityOS knowledge.
          </p>

        </div>


        <div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleUpload}
            className="hidden"
          />

          <button
            onClick={() =>
              fileInputRef.current?.click()
            }
            disabled={uploading}
            className="rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
          >

            {uploading
              ? "Processing..."
              : "Upload PDF"}

          </button>

        </div>

      </div>


      {/* ================================================= */}
      {/* Status */}
      {/* ================================================= */}

      {error && (

        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">

          {error}

        </div>

      )}


      {success && (

        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">

          {success}

        </div>

      )}


      {/* ================================================= */}
      {/* Upload Explanation */}
      {/* ================================================= */}

      <div className="rounded-xl border border-zinc-200 bg-white p-6">

        <div className="flex items-start gap-4">

          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-100 text-lg">
            PDF
          </div>

          <div>

            <h2 className="font-medium">
              Build your knowledge base
            </h2>

            <p className="mt-1 max-w-2xl text-sm leading-6 text-zinc-500">
              Upload Sarvam documentation,
              guides, FAQs, or other community
              resources. Document Intelligence
              will extract the content and turn
              useful sections into searchable
              CommunityOS knowledge.
            </p>

          </div>

        </div>

      </div>


      {/* ================================================= */}
      {/* Documents */}
      {/* ================================================= */}

      <div>

        <div className="mb-4 flex items-center justify-between">

          <h2 className="font-semibold">
            Uploaded documents
          </h2>

          <span className="text-sm text-zinc-500">
            {documents.length} documents
          </span>

        </div>


        {documents.length === 0 ? (

          <div className="rounded-xl border border-dashed border-zinc-300 bg-white px-6 py-12 text-center">

            <p className="text-sm font-medium">
              No documents uploaded
            </p>

            <p className="mt-1 text-sm text-zinc-500">
              Upload a PDF to start building
              your knowledge base.
            </p>

          </div>

        ) : (

          <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">

            <div className="divide-y divide-zinc-100">

              {documents.map(
                (document) => (

                  <div
                    key={document._id}
                    className="flex items-center justify-between px-5 py-4"
                  >

                    <div className="min-w-0">

                      <p className="truncate text-sm font-medium">
                        {document.filename}
                      </p>

                      <div className="mt-1 flex items-center gap-3 text-xs text-zinc-500">

                        <span>
                          {document.knowledge_count ?? 0}
                          {" "}
                          knowledge sections
                        </span>

                        <span>
                          {new Date(
                            document.created_at
                          ).toLocaleDateString()}
                        </span>

                      </div>

                    </div>


                    <StatusBadge
                      status={
                        document.status
                      }
                    />

                  </div>

                )
              )}

            </div>

          </div>

        )}

      </div>

    </div>
  );
}


// =========================================================
// Status Badge
// =========================================================

function StatusBadge({
  status,
}: {
  status: Document["status"];
}) {

  const styles = {

    completed:
      "bg-emerald-50 text-emerald-700",

    processing:
      "bg-amber-50 text-amber-700",

    failed:
      "bg-red-50 text-red-700",

  };

  return (

    <span
      className={`rounded-full px-2.5 py-1 text-xs font-medium ${styles[status]}`}
    >
      {status}
    </span>

  );
}