const loadedNames = ["COLUMNS", "CONNOTATIONS", "WEIGHTS"];


/**
 * @param {object[][]} rows
 */
function loadConstants(rows) {
  const constants = readSettings(rows);
  const rtv = [];

  for (const name of loadedNames) {
    if (name in constants)
      rtv.push([name].concat(constants[name]));
    else
      rtv.push([name]);
  }

  return rtv;
}
