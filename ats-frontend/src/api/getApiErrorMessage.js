const DEFAULT_MESSAGE = "Unable to process request right now. Please try again.";

function normalizeValidationError(detail) {
  if (Array.isArray(detail) && detail[0]?.msg) {
    return detail[0].msg;
  }

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  return null;
}

export default function getApiErrorMessage(error, fallback = DEFAULT_MESSAGE) {
  if (!error?.response) {
    return "Cannot connect to backend at http://127.0.0.1:8000. Start the API server and try again.";
  }

  const normalized = normalizeValidationError(error.response.data?.detail);
  if (normalized) {
    return normalized;
  }

  return fallback;
}
