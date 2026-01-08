async function loadFilters() {
  const rocketRes = await fetch('/select/rocket');
  const rockets = await rocketRes.json();
  const rocketSelect = document.getElementById('rocket');
  rockets.forEach(r => {
    rocketSelect.innerHTML += `<option value="${r.id}">${r.name}</option>`;
  });

  const launchpadRes = await fetch('/select/launchpad');
  const launchpads = await launchpadRes.json();
  const launchpadSelect = document.getElementById('launchpad');
  launchpads.forEach(l => {
    launchpadSelect.innerHTML += `<option value="${l.id}">${l.name}</option>`;
  });
}

async function loadLaunches() {
  const dateFrom = document.getElementById('date_from').value;
  const dateTo = document.getElementById('date_to').value;
  const rocket = document.getElementById('rocket').value;
  const launchpad = document.getElementById('launchpad').value;
  const success = document.getElementById('success').value;

  const params = new URLSearchParams();
  if (dateFrom) {
    const unixFrom = Math.floor(new Date(dateFrom).getTime() / 1000);
    params.append('date_from', unixFrom);
  }
  if (dateTo) {
    const unixTo = Math.floor(new Date(dateTo).getTime() / 1000);
    params.append('date_to', unixTo);
  }
  if (rocket) params.append('rocket', rocket);
  if (launchpad) params.append('launchpad', launchpad);
  if (success) params.append('success', success);

  const url = '/launches/filter?' + params.toString();
  console.log('Fetching:', url);

  const response = await fetch(url);
  const data = await response.json();
  const div = document.getElementById('launches');

  let html = '';
  data.forEach(launch => {
    html += `
      <article>
        <header><strong>${launch.name}</strong></header>
        <p><strong>Rocket:</strong> ${launch.rocket}</p>
        <p><strong>Date:</strong> ${launch.date_utc}</p>
        <p><strong>Site:</strong> ${launch.launchpad}</p>
        <p><strong>Details:</strong> ${launch.details}</p>
        <p><strong>Failures:</strong> ${launch.failures.length > 0 ? launch.failures.map(f => f.reason || 'Unknown').join(', ') : 'None'}</p>
        <p><strong>Success:</strong> ${launch.success ? '✓ Yes' : '✗ No'}</p>
      </article>
    `;
  });

  div.innerHTML = html;
}
function exportData(format) {
  const dateFrom = document.getElementById('date_from').value;
  const dateTo = document.getElementById('date_to').value;
  const rocket = document.getElementById('rocket').value;
  const launchpad = document.getElementById('launchpad').value;
  const success = document.getElementById('success').value;

  const params = new URLSearchParams();
  if (dateFrom) {
    const unixFrom = Math.floor(new Date(dateFrom).getTime() / 1000);
    params.append('date_from', unixFrom);
  }
  if (dateTo) {
    const unixTo = Math.floor(new Date(dateTo).getTime() / 1000);
    params.append('date_to', unixTo);
  }
  if (rocket) params.append('rocket', rocket);
  if (launchpad) params.append('launchpad', launchpad);
  if (success) params.append('success', success);

  const url = `/export/${format}?` + params.toString();
  window.location.href = url;
}

document.getElementById('exportCsv').addEventListener('click', () => exportData('csv'));
document.getElementById('exportJson').addEventListener('click', () => exportData('json'));

document.getElementById('date_from').addEventListener('change', loadLaunches);
document.getElementById('date_to').addEventListener('change', loadLaunches);
document.getElementById('rocket').addEventListener('change', loadLaunches);
document.getElementById('launchpad').addEventListener('change', loadLaunches);
document.getElementById('success').addEventListener('change', loadLaunches);

loadFilters();
loadLaunches();
