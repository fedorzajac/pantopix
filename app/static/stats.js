let statsData = null;
let monthlyChart = null;

async function loadStats() {
  const response = await fetch('/stats/data');
  statsData = await response.json();

  const statsDiv = document.getElementById('stats');
  statsDiv.innerHTML = `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
      <div>
        <h3>Success Rate by Rocket (%)</h3>
        <canvas id="rocketSuccessChart"></canvas>
      </div>
      <div>
        <h3>Launches by Site</h3>
        <canvas id="siteChart"></canvas>
      </div>
      <div>
        <h3>Monthly Launch Frequency</h3>
        <div style="margin-bottom: 10px;">
          <label>
            Year:
            <select id="yearSelect" onchange="updateMonthlyChart()"></select>
          </label>
        </div>
        <canvas id="monthlyChart"></canvas>
      </div>
      <div>
        <h3>Yearly Launch Frequency</h3>
        <canvas id="yearlyChart"></canvas>
      </div>
    </div>
  `;

  // Success Rate by Rocket (Bar Chart with %)
  new Chart(document.getElementById('rocketSuccessChart'), {
    type: 'bar',
    data: {
      labels: statsData.successByRocket.labels,
      datasets: [{
        label: 'Success Rate (%)',
        data: statsData.successByRocket.values.map(v => (v * 100).toFixed(1)),
        backgroundColor: '#36a2eb'
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });

  // Launches by Site (Bar Chart)
  new Chart(document.getElementById('siteChart'), {
    type: 'bar',
    data: {
      labels: statsData.launchesBySite.labels,
      datasets: [{
        label: 'Total Launches',
        data: statsData.launchesBySite.values,
        backgroundColor: '#ff6384'
      }]
    }
  });

  // Populate year dropdown
  const yearSelect = document.getElementById('yearSelect');
  statsData.frequencyByYear.labels.forEach((year, index) => {
    yearSelect.innerHTML += `<option value="${index}">${year}</option>`;
  });
  yearSelect.selectedIndex = yearSelect.options.length - 1; // Select last year

  // Monthly Chart
  updateMonthlyChart();

  // Yearly Chart
  const yearlyTotals = statsData.frequencyByYear.values.map(months =>
    months.reduce((sum, val) => sum + val, 0)
  );

  new Chart(document.getElementById('yearlyChart'), {
    type: 'line',
    data: {
      labels: statsData.frequencyByYear.labels,
      datasets: [{
        label: 'Launches per Year',
        data: yearlyTotals,
        borderColor: '#4bc0c0',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
        fill: true
      }]
    }
  });
}

function updateMonthlyChart() {
  const yearIndex = document.getElementById('yearSelect').value;
  const monthlyData = statsData.frequencyByYear.values[yearIndex];
  const year = statsData.frequencyByYear.labels[yearIndex];

  if (monthlyChart) {
    monthlyChart.destroy();
  }

  monthlyChart = new Chart(document.getElementById('monthlyChart'), {
    type: 'bar',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      datasets: [{
        label: `Launches in ${year}`,
        data: monthlyData,
        backgroundColor: '#9966ff'
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

loadStats();
