const renderValue = (value: any) => {
  if (Array.isArray(value)) {
    return (
      <ul className="list-disc ml-5">
        {value.map((item, idx) => (
          <li key={idx}>{typeof item === "object" ? renderObject(item) : item}</li>
        ))}
      </ul>
    );
  } else if (typeof value === "object" && value !== null) {
    return renderObject(value);
  }
  return <span>{value}</span>;
};

const renderObject = (obj: Record<string, any>) => {
  return (
    <div className="pl-4">
      {Object.entries(obj).map(([key, value], idx) => (
        <div key={idx} className="mb-2">
          <strong>{key}:</strong> {renderValue(value)}
        </div>
      ))}
    </div>
  );
};

export const ExtractedDataTable = ({ records }: { records: any[] }) => {
  return (
    <div className="mt-8 space-y-6">
      {records.map((record, idx) => (
        <div key={idx} className="p-4 bg-white border rounded shadow">
          <h3 className="text-lg font-bold mb-2">Filename: {record.filename}</h3>
          {renderObject(record.extracted_data)}
        </div>
      ))}
    </div>
  );
};

export default ExtractedDataTable;
