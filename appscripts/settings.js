/**
 * @param {object[][]} rows The rows to read the settings from.
 */
function readSettings(rows) {
  const rtv = {};
  for (const row of rows) {
    const name = row[0];
    if (!(typeof name == "string" && name))
      continue;

    const values = [];
    let lastValue = -1;
    let index = 0;
    for (const value of row.slice(1)) {
      values.push(value);
      if (typeof value != "string" || value) //if not a string, or is a string and is not empty
        lastValue = index;
      index++;
    }

    const realValues = lastValue==(values.length-1) ? values : values.slice(0, lastValue+1);
    if (realValues.length == 0)
      rtv[name] = null;
    else if (realValues.length == 1)
      rtv[name] = realValues[0];
    else
      rtv[name] = realValues;
  }
  return rtv;
}
