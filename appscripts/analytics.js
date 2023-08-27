/**
 * @param {object[][]} rows Rows to grab using each value in the designated "ID COLUMN" as the key.
 * @param {string[][]} columns The column names for the given rows.
 * @returns {Map<object, object[][]>} The map of "ID COLUMN" value to an array of arrays for each value of each column.
 */
function grabAll(idColumnName, rows, columns) {
    /*
    {id : [
        [], (per column)
        ...
      ], (per unique id)...
    }
    */
    const rtv = new Map();
  
    columns = columns[0];
    const endColumns = columns.indexOf("");
    if (endColumns > -1)
      columns = columns.slice(0, endColumns);
    const idColumn = columns.indexOf(idColumnName);
  
    for (const row of rows) {
      //grab row id
      const id = row[idColumn];
      if (typeof id == "string" && !id) continue;
      if (!rtv.has(id))
        //length-1 to exclude id row
        rtv.set(id, new Array(columns.length-1).fill(0).map(_ => []));
  
      let indexOffset = 0;
      for (let i = 0; i < columns.length; i++) {
        if (i == idColumn) {
          indexOffset = 1;
          continue; //ID column does not need to be evaluated
        }
        
        rtv.get(id)[i-indexOffset].push(row[i]);
      }
    }
  
    return rtv;
}

/**
 * @param {string} columnName Limit Column name.
 * @param {string|object} min
 * @param {string|object} max
 * @param {object[][]} rows
 * @param {string[][]} columns
 */
function limitRows(columnName, min, max, rows, columns) {
    const limitColumn = columns[0].indexOf(columnName);
    const rtv = [];

    if (min == LIMIT_MIN && max == LIMIT_MAX) return rows; //all values in limit: no change
    const hasMap = columnName in valMap;

    //convert min and max for comparison
    if (min != LIMIT_MIN && min != LIMIT_MAX && typeof min != "number" && typeof min != "boolean") {
        if (!hasMap) throw new Error(`Limit Bottom ${min} cannot be used to check for limit.`);
        min = valMap[columnName](min);
    }
    if (max != LIMIT_MAX && max != LIMIT_MIN && typeof max != "number" && typeof max != "boolean") {
        if (!hasMap) throw new Error(`Limit Top ${max} cannot be used to check for limit.`);
        max = valMap[columnName](max);
    }

    //include rows within min and max
    for (const row of rows) {
        let value = row[limitColumn];

        if (typeof value != "number" && typeof value != "boolean") {
        //cannot convert to numeric for comparison
        if (!(columnName in valMap)) throw new Error(`Value ${value} in column "${columnName}" cannot be checked for limit.`);
        value = valMap[columnName](value);
        }
        
        if ((min==LIMIT_MIN || value>=min) && (max==LIMIT_MAX || value <= max))
        rtv.push(row);
    }

    return rtv;
}

/**
 * @param {Map<object, object[][]>} map The columns per ID to compress.
 * @returns {Map<object, object[]>}
 */
function compressAvg(map) {
    const rtv = new Map();

    map.forEach((value, key) => {
        const rtvColumns = [];
        for (const column of value) {
        //all numeric, get average
        if (column.every(v => typeof v == "number"))
            rtvColumns.push(column.reduce((part, a) => part+a, 0)/column.length);
        //get mode
        else {
            const count = new Map();
            for (const item of column) {
            if (count.has(item))
                count.set(item, count.get(item)+1);
            else
                count.set(item, 1);
            }
            let max = null;
            count.forEach((cval, ckey) => {
            const current = count.get(max);
            if (max==null || cval > current || (cval == current && column.indexOf(ckey) < column.indexOf(max)))
                max = ckey;
            });
            rtvColumns.push(max);
        }
        }

        rtv.set(key, rtvColumns);
    });

    return rtv;
}

/**
 * @param {Map<object, object[][]> map The columns per ID to compress.
 * @returns {Map<object, object[]>} 
 */
function compressMax(map) {
    const rtv = new Map();

    map.forEach((value, key) => {
        const rtvColumns = [];
        for (const column of value) {
        if (column.every(v => typeof v == "number"))
            rtvColumns.push(Math.max(...column));
        else if (column.every(v => typeof v == "boolean"))
            rtvColumns.push(column.includes(true));
        else {
            const count = new Map();
            for (item of column) {
            if (count.has(item))
                count.set(item, count.get(item)+1);
            else
                count.set(item, 1);
            }
            
            let max = null;
            count.forEach((cval, ckey) => {
            const current = count.get(max);
            if (max==null || cval > current || (cval == current && column.indexOf(ckey) < column.indexOf(max)))
                max = ckey;
            });

            rtvColumns.push(max);
        }
        }

        rtv.set(key, rtvColumns);
    });

    return rtv;
}

/**
 * @param {Map<object, object[][]> map The columns per ID to compress.
 * @returns {Map<object, object[]>} 
 */
function compressMin(map) {
    const rtv = new Map();

    map.forEach((value, key) => {
        const rtvColumns = [];
        for (const column of value) {
        if (column.every(v => typeof v == "number"))
            rtvColumns.push(Math.min(...column));
        else if (column.every(v => typeof v == "boolean"))
            rtvColumns.push(!column.includes(false));
        else {
            const count = new Map();
            for (item of column) {
            if (count.has(item))
                count.set(item, count.get(item)+1);
            else
                count.set(item, 1);
            }
            
            let min = null;
            count.forEach((cval, ckey) => {
            const current = count.get(min);
            if (min==null || cval < current || (cval == current && column.indexOf(ckey) < column.indexOf(min)))
                min = ckey;
            });

            rtvColumns.push(min);
        }
        }

        rtv.set(key, rtvColumns);
    });

    return rtv;
}

/**
 * @param {object[][]} rows Rows to find the average of using each value in the designated "ID COLUMN" as the key.
 * @param {object[][]} columns The column names for the given rows.
 * @returns {Map<object, object[]>} The map of "ID COLUMN" value to found average. Numeric values will be the average of those values, while non-numeric values will be the mode.
 */
function grabAvg(idColumnName, rows, columns) {
    return compressAvg(grabAll(idColumnName, rows, columns));
}

/**
 * @param {object[][]} rows Rows to find the max of using each value in the designated "ID COLUMN" as the key.
 * @param {object[][]} columns The column names for the given rows.
 * @returns {Map<object, object[]>} The map of "ID COLUMN" value to found max. Numeric values will be the largest of those values, while non-numeric values will be the mode.
 */
function grabMax(idColumnName, rows, columns) {
    return compressMax(grabAll(idColumnName, rows, columns));
}

/**
 * @param {object[][]} rows Rows to find the min of using each value in the designated "ID COLUMN" as the key.
 * @param {object[][]} columns The column names for the given rows.
 * @returns {Map<object, object[]>} The map of "ID COLUMN" value to found min. Numeric values will be the smallest of those values, while non-numeric values will be the least frequently appearing values (anti-mode).
 */
function grabMin(idColumnName, rows, columns) {
    return compressMin(grabAll(idColumnName, rows, columns));
}
