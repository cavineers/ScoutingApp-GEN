/**
 * @param {object[][]} members
 * @param {number} memberCount
 * @param {object} limitMin
 * @param {object} limitMax
 * @param {string} compressMethod
 * @param {string} idColumnName
 * @param {string} limitColumnName
 * @param {object[][]} rows
 * @param {string[][]} columns
 */
function multiViewUI(members, memberCount, limitMin, limitMax, compressMethod, idColumnName, limitColumnName, rows, columns) {
  const rtv = [];

  //trim members
  members = members[0].slice(0, memberCount*2);

  //make sure that members are unique
  if (members.includes("")) return `Expected ${memberCount} members per group (${memberCount*2} total), make sure that all member IDs have been filled.`;
  if ((new Set(members)).size != members.length) return "Member IDs must be unique."

  const limited = limitRows(limitColumnName, limitMin, limitMax, rows, columns);
  
  let grabbed;
  switch (compressMethod.toUpperCase()) {
    case "AVG": grabbed = grabAvg(idColumnName, limited, columns); break;
    case "MAX": grabbed = grabMax(idColumnName, limited, columns); break;
    case "MIN": grabbed = grabMin(idColumnName, limited, columns); break;
    default:
      throw new Error(`Invalid compress method "${compressMethod}".`);
  }

  //get limit column to skip
  const idColumn = columns[0].indexOf(idColumnName);
  let limitColumn = columns[0].indexOf(limitColumnName);
  if (limitColumn > idColumn) limitColumn--;

  const columnLength = grabbed.get(members[0]).length;
  for (let i = 0; i<columnLength; i++) {
    if (i==limitColumn) continue;

    const column = [];
    for (const member of members)
      column.push(grabbed.has(member) ? grabbed.get(member)[i] : "");
    rtv.push(column);
  }
  if (rtv.length == 0) return "Enter Members.";
  return rtv;
}

/**
 * @param {number} teamNumber
 * @param {number} memberCount
 * @param {string} idColumnName
 * @param {string} limitColumnName
 * @param {object[][]} rows
 * @param {string[][]} columns
 * @param {number[][]|string[][]} weights
 */
function getScore(teamNumber, memberCount, idColumnName, limitColumnName, rows, columns, weights) {
  columns = columns[0];
  weights = weights[0];

  //trim columns
  const endColumns = columns.indexOf("");
  if (endColumns>-1)
    columns = columns.slice(0,endColumns);

  //remove id and limit columns
  const idColumn = columns.indexOf(idColumnName);
  let limitColumn = columns.indexOf(limitColumnName);
  if (limitColumn > idColumn) limitColumn--;
  if (idColumn>-1) {
    columns.splice(idColumn, 1);
    weights.splice(idColumn, 1);
  }
  if (limitColumn>-1) {
    columns.splice(limitColumn, 1);
    weights.splice(limitColumn, 1);
  }

  let totalScore = 0;
  for (let i = 0; i < columns.length; i++) {
    const columnName = columns[i];
    const weight = weights[i] === "" || weights[i] === undefined ? 0 : weights[i];
    
    //slice row to get team values
    const row = rows[i].slice(0, memberCount*2);
    const sliced = row.slice(memberCount*(teamNumber-1), memberCount*teamNumber);
    //column numeric converstion data
    const isNumeric = row.every(v => typeof v == "number" || typeof v == "boolean");
    const mapFunc = valMap[columnName];

    //per value in sliced (value -> numeric form * weight) -> sum = score
    totalScore += sliced.map(v => isNumeric ? v : mapFunc !== undefined ? mapFunc(v) : 0).reduce((pv, cv) => pv+cv, 0)*weight;
  }

  return totalScore/memberCount;
}
