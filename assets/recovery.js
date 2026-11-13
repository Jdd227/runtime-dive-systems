(() => {
  const form = document.getElementById('recoveryform');
  if (!form) return;
  const recipient = 'innerspacescubasociety@gmail.com';
  const preview = document.getElementById('preview');
  const fields = [
    ['category', 'Item type'], ['details', 'Description'], ['lostdate', 'Date lost'],
    ['location', 'Location'], ['depth', 'Estimated depth'], ['access', 'Access'],
    ['coordinates', 'Map pin'], ['person', 'Name'], ['email', 'Email'],
    ['phone', 'Phone'], ['urgency', 'Timeline']
  ];
  function requestDetails() {
    const data = new FormData(form);
    return {
      data,
      summary: fields.map(([key, label]) => label + ': ' + (data.get(key) || 'Not supplied')).join('\n')
    };
  }
  document.getElementById('previewbutton').addEventListener('click', () => {
    if (!form.reportValidity()) return;
    preview.textContent = 'To: ' + recipient + '\nSubject: RunTime Recovery Inquiry\n\n' + requestDetails().summary;
    preview.classList.add('visible');
  });
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const { data, summary } = requestDetails();
    const subject = 'RunTime Recovery Inquiry: ' + (data.get('category') || 'New request');
    const body = summary;
    window.location.href = 'mailto:' + recipient + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    preview.textContent = 'Your email application should open with the request. Press Send to submit it. If nothing opened, email ' + recipient + ' directly.';
    preview.classList.add('visible');
  });
})();
