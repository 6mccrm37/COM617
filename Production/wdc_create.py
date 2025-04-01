from pathlib import Path

# Define the full HTML content
wdc_html = """<!DOCTYPE html>
<html>
<head>
  <title>Py6S Tableau Web Data Connector</title>
  <script src="https://connectors.tableau.com/libs/tableauwdc-2.3.latest.js"></script>
</head>
<body>
  <h1>Py6S Data Connector</h1>
  <form id="py6s-form">
    <label>Latitude: <input type="number" id="latitude" step="0.01" value="50"></label><br>
    <label>Date (YYYY-MM-DD): <input type="text" id="date" value="2024-07-14"></label><br>
    <label>AOT550: <input type="number" id="aot550" step="0.1" value="0.1"></label><br>
    <label>Sensor:
      <select id="sensor">
        <option value="landsat_etm">Landsat ETM</option>
        <option value="vnir">VNIR</option>
      </select>
    </label><br><br>
    <button type="button" onclick="submitToTableau()">Load Data in Tableau</button>
  </form>

  <script>
    function submitToTableau() {
      var latitude = parseFloat(document.getElementById('latitude').value);
      var date = document.getElementById('date').value;
      var aot550 = parseFloat(document.getElementById('aot550').value);
      var sensor = document.getElementById('sensor').value;

      tableau.connectionName = "Py6S Radiance Data";
      tableau.connectionData = JSON.stringify({ latitude, date, aot550, sensor });
      tableau.submit();
    }

    var myConnector = tableau.makeConnector();

    myConnector.getSchema = function (schemaCallback) {
      var cols = [
        { id: "wavelength", alias: "Wavelength (μm)", dataType: tableau.dataTypeEnum.float },
        { id: "radiance", alias: "Radiance (W/m²/sr/μm)", dataType: tableau.dataTypeEnum.float }
      ];
      var tableSchema = {
        id: "py6sRadiance",
        alias: "Radiance vs Wavelength",
        columns: cols
      };
      schemaCallback([tableSchema]);
    };

    myConnector.getData = function (table, doneCallback) {
      var params = JSON.parse(tableau.connectionData);
      fetch("/run-model", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
      })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          tableau.abortWithError("Py6S model error: " + data.error);
          return;
        }
        var tableData = [];
        for (var i = 0; i < data.wavelengths.length; i++) {
          tableData.push({
            wavelength: data.wavelengths[i],
            radiance: data.radiance[i]
          });
        }
        table.appendRows(tableData);
        doneCallback();
      })
      .catch(error => {
        tableau.abortWithError("Request failed: " + error);
      });
    };

    tableau.registerConnector(myConnector);
  </script>
</body>
</html>
"""

# Save it to the correct directory
file_path = Path("C:/Users/Martin/PycharmProjects/PythonProject1/Production/wdc/connector.html")
file_path.write_text(wdc_html, encoding="utf-8")
print(f" WDC file created at: {file_path}")
