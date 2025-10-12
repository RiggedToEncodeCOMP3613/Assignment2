document.addEventListener('DOMContentLoaded', function() {
  const selectDriver = document.getElementById('select-driver');
  const selectResident = document.getElementById('select-resident');
  const selectDrive = document.getElementById('select-drive');
  const selectStreet = document.getElementById('select-street');
  const output = document.getElementById('output');
  const tableSchedule = document.getElementById('table-schedule');
  const tableInbox = document.getElementById('table-inbox');
  const tableAll = document.getElementById('table-all');
  const tableDrives = document.getElementById('table-drives');

  function appendOutput(txt) {
    const ts = new Date().toISOString();
    output.textContent = `[${ts}] ${txt}\n` + output.textContent;
  }

  // Fetch full snapshot (drivers, residents, drives, stop_requests) and populate all selects/tables
  async function refreshAll() {
    try {
      const res = await fetch('/api/transport/list-all');
      const data = await res.json();

      // drivers
      selectDriver.innerHTML = '<option value="" disabled selected>Choose driver</option>';
      (data.drivers || []).forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.id;
        opt.text = `#${d.id} - ${d.status || ''}`;
        selectDriver.appendChild(opt);
      });

      // residents
      selectResident.innerHTML = '<option value="" disabled selected>Choose resident</option>';
      (data.residents || []).forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.id;
        opt.text = `#${r.id} - ${r.name || ''} ${r.street ? '('+r.street+')' : ''}`;
        selectResident.appendChild(opt);
      });

      // drives
      selectDrive.innerHTML = '<option value="" disabled selected>Choose drive</option>';
      tableDrives.innerHTML = '';
      (data.drives || []).forEach(dr => {
        const opt = document.createElement('option');
        opt.value = dr.id;
        opt.text = `#${dr.id} - ${dr.datetime || ''}`;
        selectDrive.appendChild(opt);

        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${dr.id}</td><td>${dr.datetime}</td><td>${dr.driver_id}</td><td>${dr.current_location || ''}</td>`;
        tableDrives.appendChild(tr);
      });

      // streets: collect unique streets from residents and stop_requests
      const streets = new Set();
      (data.residents || []).forEach(r => { if (r.street) streets.add(r.street); });
      (data.stop_requests || []).forEach(s => { if (s.street_name) streets.add(s.street_name); });
      selectStreet.innerHTML = '<option value="" disabled selected>Choose street</option>';
      Array.from(streets).forEach(s => {
        const opt = document.createElement('option');
        opt.value = s;
        opt.text = s;
        selectStreet.appendChild(opt);
      });

      // All Data table (compact JSON rows)
      tableAll.innerHTML = '';
      Object.entries(data).forEach(([key, arr]) => {
        const tr = document.createElement('tr');
        const tdType = document.createElement('td');
        tdType.textContent = key;
        const tdData = document.createElement('td');
        tdData.textContent = JSON.stringify(arr, null, 2);
        tr.appendChild(tdType);
        tr.appendChild(tdData);
        tableAll.appendChild(tr);
      });

      appendOutput('Refreshed options and lists');
    } catch (e) {
      appendOutput('Failed to refresh data: ' + e.message);
    }
  }

  async function createResident() {
    const name = document.getElementById('new-resident-name').value || null;
    const chosenStreet = selectStreet.value || '';
    const typed = document.getElementById('new-resident-street').value || '';
    const street = typed ? typed : (chosenStreet || null);
    const res = await fetch('/api/transport/create-resident', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, street })
    });
    const data = await res.json();
    appendOutput('Created resident: ' + JSON.stringify(data));
    await refreshAll();
  }

  async function createDriver() {
    const status = document.getElementById('new-driver-status').value || null;
    const res = await fetch('/api/transport/create-driver', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    const data = await res.json();
    appendOutput('Created driver: ' + JSON.stringify(data));
    await refreshAll();
  }

  async function createDrive() {
    const driver_id = parseInt(selectDriver.value);
    const location = document.getElementById('new-drive-location').value || null;
    const when = null;
    if (!driver_id) { appendOutput('Select a driver first'); return; }
    const res = await fetch('/api/transport/create-drive', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ driver_id, when, location })
    });
    const data = await res.json();
    if (res.ok) {
      appendOutput('Created drive: ' + JSON.stringify(data));
      await refreshAll();
    } else {
      appendOutput('Failed to create drive: ' + JSON.stringify(data));
    }
  }

  async function createStop() {
    const resident_id = parseInt(selectResident.value);
    const drive_id = parseInt(selectDrive.value);
    const street = document.getElementById('new-stop-street').value || null;
    if (!resident_id || !drive_id) { appendOutput('Select resident and drive first'); return; }
    const res = await fetch('/api/transport/create-stop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resident_id, drive_id, street })
    });
    const data = await res.json();
    if (res.ok) {
      appendOutput('Created stop: ' + JSON.stringify(data));
      await refreshAll();
    } else {
      appendOutput('Failed to create stop: ' + JSON.stringify(data));
    }
  }

  // Modal logic for editing drive
  const editDriveModal = document.getElementById('edit-drive-modal');
  const editDriveForm = document.getElementById('edit-drive-form');
  let modalInstance = null;
  if (window.M && M.Modal) {
    modalInstance = M.Modal.init(editDriveModal, {});
  }

  // Render edit buttons in schedule table
  async function showSchedule() {
    const driver_id = parseInt(selectDriver.value);
    if (!driver_id) { appendOutput('Select a driver first'); return; }
    const res = await fetch(`/api/transport/driver-schedule?driver_id=${driver_id}`);
    const data = await res.json();
    tableSchedule.innerHTML = '';
    data.forEach(d => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${d.id}</td><td>${d.datetime}</td><td>${(d.stops||[]).join(', ')}</td><td>${d.current_location||''}</td><td><button class='btn-small edit-drive-btn' data-id='${d.id}' data-datetime='${d.datetime}' data-location='${d.current_location||''}'>Edit</button></td>`;
      tableSchedule.appendChild(tr);
    });
    // Attach edit handlers
    document.querySelectorAll('.edit-drive-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        document.getElementById('edit-drive-id').value = btn.getAttribute('data-id');
        document.getElementById('edit-drive-datetime').value = btn.getAttribute('data-datetime').slice(0, 16); // ISO string to yyyy-MM-ddTHH:mm
        document.getElementById('edit-drive-location').value = btn.getAttribute('data-location');
        if (modalInstance) modalInstance.open();
        else editDriveModal.style.display = 'block';
      });
    });
    appendOutput('Driver schedule loaded');
  }

  // Handle drive update form submit
  editDriveForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const id = document.getElementById('edit-drive-id').value;
    const datetime = document.getElementById('edit-drive-datetime').value;
    const location = document.getElementById('edit-drive-location').value;
    const res = await fetch(`/api/transport/update-drive`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, datetime, location })
    });
    const data = await res.json();
    if (res.ok) {
      appendOutput('Drive updated: ' + JSON.stringify(data));
      if (modalInstance) modalInstance.close();
      else editDriveModal.style.display = 'none';
      await showSchedule();
      await refreshAll();
    } else {
      appendOutput('Failed to update drive: ' + JSON.stringify(data));
    }
  }

  async function showInbox() {
    const resident_id = parseInt(selectResident.value);
    const street = document.getElementById('new-stop-street').value || '';
    if (!resident_id) { appendOutput('Select a resident first'); return; }
    const url = `/api/transport/resident-inbox?resident_id=${resident_id}` + (street ? `&street=${encodeURIComponent(street)}` : '');
    const res = await fetch(url);
    const data = await res.json();
    tableInbox.innerHTML = '';
    data.forEach(s => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${s.id}</td><td>${s.street_name}</td><td>${s.drive_id}</td><td>${s.created_at}</td>`;
      tableInbox.appendChild(tr);
    });
    appendOutput('Resident inbox loaded');
  }

  // wire buttons
  document.getElementById('btn-create-resident').addEventListener('click', createResident);
  document.getElementById('btn-create-driver').addEventListener('click', createDriver);
  document.getElementById('btn-create-drive').addEventListener('click', createDrive);
  document.getElementById('btn-create-stop').addEventListener('click', createStop);
  document.getElementById('btn-show-schedule').addEventListener('click', showSchedule);
  document.getElementById('btn-show-inbox').addEventListener('click', showInbox);

  // initial load
  refreshAll();
});