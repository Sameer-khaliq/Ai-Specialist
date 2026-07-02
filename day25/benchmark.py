import time, os, json
from extractor import extract_from_image, validate_extraction

test_dir = "day25/test_images"
results = []

for fname in os.listdir(test_dir):
    path = os.path.join(test_dir, fname)
    start = time.time()
    result = extract_from_image(path)
    latency = time.time() - start
    validated = validate_extraction(result)
    results.append({
        "file": fname,
        "type_detected": result.document_type,
        "confidence": result.confidence,
        "latency_sec": round(latency, 2),
        "fields_extracted": len(validated) if isinstance(validated, dict) else 0
    })

print(json.dumps(results, indent=2))
avg_latency = sum(r["latency_sec"] for r in results) / len(results)
print(f"\nAvg latency: {avg_latency:.2f}s across {len(results)} images")