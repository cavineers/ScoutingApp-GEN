/**
 * @param {string} mode
 * @param {string} columnName
 * @param {object[][]} column
 * @param {number} memberCount
 */
function graphRange(mode, columnName, column, memberCount) {
  if (mode===undefined || mode===null) mode = "column";
  else mode = mode.toLowerCase();
  if(memberCount===undefined || mode===null) memberCount = 0;

  let numeric;
  
  if (!Array.isArray(column))
    return [0];
  if (column.every(v => typeof v[0] == "number" || typeof v[0] == "boolean"))
    numeric = column;
  else if (columnName in valMap) {
    const m = valMap[columnName];
    numeric = column.map(v => [m(v[0])]);
  }
  else
    numeric = column.map(v => [0]); //if values cannot become numeric, set all to 0

  if (mode=="winloss") {
    //find average, negative if less than avg, else positive
    const winloss = [];

    for (let g = 0; g<2; g++) {
      const slice = memberCount ? numeric.slice(g*memberCount, (g+1)*memberCount) : numeric;
      const avg = slice.reduce((p,c) => p+c[0], 0)/slice.length;
      
      for (const data of slice)
        winloss.push([Math.abs(data[0])* (data[0] < avg ? -1 : data[0] == avg ? 0 : 1)]);

      if (!memberCount)
        break;
    }
    return winloss;
  }
  else if (mode=="column" || mode=="line") {
    return numeric;
  }
  else
    throw new Error(`Invalid mode "${mode}".`);
}

/**
 * @param {string} mode
 * @param {string} columnName
 * @param {string[][]} columns
 * @param {boolean[][]|string[][]} connotations
 */
function graphOptions(mode, columnName, columns, connotations) {
  let conn = connotations[0][columns[0].indexOf(columnName)];
  if (conn === undefined || conn === "") conn = true;
  
  const lowcolor = conn ? "red" : "lightgreen";
  const highcolor = conn ? "lightgreen" : "red";
  return [["charttype", mode.toLowerCase()], ["color", "lightgray"], ["lowcolor", lowcolor], ["highcolor", highcolor]];
}
