function individualViewUI(idColumnName, limitColumnName, id, limitMin, limitMax, rows, columns) {
  if (id == "") return "Enter ID.";
  
  const idColumn = columns[0].indexOf(idColumnName);
  const limitColumn = columns[0].indexOf(limitColumnName);

  //limit rows
  rows = limitRows(limitColumnName, limitMin, limitMax, rows, columns);

  //grab only rows with matching id, while removing id and limit columns
  const rtv = [];
  for (const row of rows) {
    if (row[idColumn] == id) {
      row.splice(idColumn, 1);
      row.splice(limitColumn > idColumn ? limitColumn-1 : limitColumn, 1);
      rtv.push(row);
    }
  }

  if (rtv.length<1) return "No data found.";

  return rtv;

}

/**
 * @param {object[][]} rows
 * @param {string} idColumnName
 * @param {string[][]} columns
 */
function getIDRange(rows, idColumnName, columns) {
  const idColumn = columns[0].indexOf(idColumnName);
  const rtv = [];

  for (const row of rows) {
    const id = row[idColumn];
    if (!rtv.includes(id))
      rtv.push(id);
  }
  return [rtv];
}