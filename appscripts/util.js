/**
 * @param {object[][]} values Swap columns and rows in the values.
 * @returns {object[][]}
 */
function transpose(values) {
    return Object.keys(values[0]).map(c => values.map(r => r[c]));
}
