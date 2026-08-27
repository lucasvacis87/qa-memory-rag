const data = window.QA_MEMORY_SAMPLES.samples;
const select = document.querySelector('#case-select');
const result = document.querySelector('#result');

const caseTranslations = {
  'UC-01': ['The user is locked out before the fifth attempt', 'The retrieved evidence (BUG-AUT-001, BUG-PAG-003, TC-AUT-001, TC-TRF-003) contains related history and coverage. Review those records and run only the cited test cases; interpret technical details according to their evidence status.'],
  'UC-02': ['An approved transfer does not appear in transaction history', 'The retrieved evidence (BUG-MOV-001, BUG-MOV-002, TC-MOV-001, TC-MOV-003) contains related history and coverage. Review those records and run only the cited test cases; interpret technical details according to their evidence status.'],
  'UC-03': ['A rejected transfer deducts the balance', 'The retrieved evidence (BUG-TRF-001, BUG-MOV-001, TC-TRF-007, TC-TRF-004) contains related history and coverage. Review those records and run only the cited test cases; interpret technical details according to their evidence status.'],
  'UC-04': ['A service payment is charged twice after retrying', 'The retrieved evidence (BUG-PAG-001, BUG-PAG-002, TC-PAG-004, TC-PAG-002) contains related history and coverage. Review those records and run only the cited test cases; interpret technical details according to their evidence status.'],
  'UC-05': ['The card limit changes in the interface but not in the backend', 'The retrieved evidence (BUG-TAR-001, BUG-AUT-002, TC-TAR-002, TC-TAR-001) contains related history and coverage. Review those records and run only the cited test cases; interpret technical details according to their evidence status.'],
  'UC-06': ['A successful operation generates neither a receipt nor a notification', 'The retrieved evidence (BUG-NOT-001, BUG-NOT-002, TC-NOT-002, TC-NOT-003) contains related history and coverage. Review those records and run only the cited test cases; interpret technical details according to their evidence status.'],
  'UC-07': ['Which existing regression covers duplicate transfer submissions?', 'The retrieved evidence (BUG-TRF-002, BUG-TRF-003, TC-TRF-001, TC-TRF-003) contains related history and coverage. Review those records and run only the cited test cases; interpret technical details according to their evidence status.'],
  'UC-08': ['How do I grow orchids on Mars?', 'There is not enough evidence in the knowledge base to provide a traceable answer.']
};

const recordTranslations = {
  'BUG-AUT-001': ['Premature lockout on the fourth attempt', 'Failed-attempt counter increments twice when an invalid-credential response takes more than two seconds, locking the user out one attempt too early.'],
  'BUG-PAG-003': ['Expiry date interpreted in the wrong time zone', 'An invoice valid through the end of the local day is marked expired hours early because its date is interpreted in UTC.'],
  'TC-AUT-001': ['Five failed attempts and lockout', 'Enter invalid credentials four times and confirm the account remains enabled; on the fifth invalid attempt, verify the lockout.'],
  'TC-TRF-003': ['Fee visible before confirmation', 'Request a quote with a fee and verify that principal, fee, and total are visible and match the response before confirming.'],
  'BUG-MOV-001': ['Approved transfer missing from transaction history', 'An approved transfer updates the available balance but does not immediately create its corresponding transaction entry.'],
  'BUG-MOV-002': ['Duplicate transaction while paginating', 'The final transaction of the first history page is shown again as the first item of the second page.'],
  'TC-MOV-001': ['Approved operation appears in history', 'Create an approved transfer, capture its ID, and verify one matching history entry and balance update.'],
  'TC-MOV-003': ['Pagination without repeated transactions', 'Load enough transactions for two pages and verify that no ID from the first page is repeated on the second.'],
  'BUG-TRF-001': ['Rejected transfer deducts balance', 'When the receiving bank rejects a transfer, the debit remains applied and no reversal is recorded.'],
  'TC-TRF-007': ['Rejected-transfer reversal', 'Run a controlled post-authorization rejection and verify its compensating entry leaves a net total of zero.'],
  'TC-TRF-004': ['Rejection does not deduct balance', 'Record the opening balance, cause a controlled rejection, and verify the final balance is unchanged.'],
  'BUG-PAG-001': ['Duplicate payment after retry', 'A delayed response invites a retry even though the first payment was accepted, producing a second debit for the same invoice.'],
  'BUG-PAG-002': ['Rejected payment remains pending', 'The provider rejects the operation, but the interface keeps it pending until the user starts a new session.'],
  'TC-PAG-004': ['Expiry uses local date', 'Validate an invoice during the final local hours of its due date and repeat after the day changes.'],
  'TC-PAG-002': ['One debit and one receipt per invoice', 'Pay a fictional invoice and verify exactly one debit and one receipt point to the same payment reference.'],
  'BUG-TAR-001': ['Limit updated only in the interface', 'The interface confirms a card-limit increase, but a later service query returns the previous limit.'],
  'BUG-AUT-002': ['Unlock does not reset the counter', 'After a successful unlock, the visible status is active but the internal counter still retains four failed attempts.'],
  'TC-TAR-002': ['Backend rejects an invalid limit', 'Send a value outside the declared rules and verify the service rejects it without changing the current limit.'],
  'TC-TAR-001': ['Limit change persists', 'Request a permitted fictional limit, confirm the change, and query it again from a new session.'],
  'BUG-NOT-001': ['Successful operation without a receipt', 'A transfer completes successfully, but the receipt service returns no associated document.'],
  'BUG-NOT-002': ['Notification sent twice', 'The consumer processes the same event twice and sends duplicate email notifications with the same operation ID.'],
  'TC-NOT-002': ['Query for a missing receipt', 'Request a non-existent fictional receipt ID and verify a controlled response without an invented document.'],
  'TC-NOT-003': ['An event generates one notification', 'Publish a fictional successful-operation event and verify a single notification is associated with its ID.'],
  'BUG-TRF-002': ['Duplicate submission after repeated confirmation', 'Two quick confirmations create separate transfers because the second request does not reuse the idempotency key.'],
  'BUG-TRF-003': ['Fee omitted from confirmation', 'The confirmation screen shows the principal amount but omits the fee reported by the service.'],
  'TC-TRF-001': ['Single confirmation on double-click', 'Complete a transfer and confirm twice in quick succession; verify one approved operation, one ID, and one debit.']
};

const moduleTranslations = {
  'Autenticación': 'Authentication', 'Pago de servicios': 'Service payments', 'Saldos y movimientos': 'Balances and transactions',
  'Transferencias': 'Transfers', 'Tarjetas y límites': 'Cards and limits', 'Notificaciones y comprobantes': 'Notifications and receipts'
};

for (const sample of data) {
  const option = document.createElement('option');
  option.value = sample.case_id;
  option.textContent = `${sample.case_id} · ${caseTranslations[sample.case_id][0]}`;
  select.append(option);
}

const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
}[char]));

const splitIds = value => String(value || '').split(',').map(id => id.trim()).filter(Boolean);

const getTranslation = chunk => recordTranslations[chunk.id] || [chunk.metadata?.title || chunk.id, chunk.content];

function renderRelations(relatedIds) {
  const ids = splitIds(relatedIds);
  if (!ids.length) return '<span class="empty-value">No recorded relationships</span>';
  return ids.map(id => `<span class="id-chip">${escapeHtml(id)}</span>`).join('');
}

function renderChunk(chunk) {
  const metadata = chunk.metadata || {};
  const isBug = chunk.type === 'bug';
  const relevance = Math.round(Number(chunk.score) * 100);
  const typeLabel = isBug ? 'Bug' : 'Test case';
  const [title, summary] = getTranslation(chunk);
  const module = moduleTranslations[chunk.module] || chunk.module;

  return `
    <article class="chunk chunk--${isBug ? 'bug' : 'test'}">
      <div class="chunk-head">
        <span class="chunk-id">${escapeHtml(chunk.id)}</span>
        <span class="type-badge">${typeLabel}</span>
      </div>
      <h4>${escapeHtml(title)}</h4>
      <p class="chunk-summary">${escapeHtml(summary)}</p>
      <dl class="facts">
        <div><dt>Module</dt><dd>${escapeHtml(module)}</dd></div>
        <div><dt>Operation</dt><dd><code>${escapeHtml(metadata.endpoint_or_operation || 'Not provided')}</code></dd></div>
        <div><dt>Owner</dt><dd>${escapeHtml(`QA team — ${module}`)}</dd></div>
        <div><dt>Relationships</dt><dd class="relations">${renderRelations(metadata.related_ids)}</dd></div>
      </dl>
      <div class="evidence-row">
        <span class="evidence-badge">● Evidence ${escapeHtml(metadata.evidence_state === 'confirmado' ? 'confirmed' : 'unknown')}</span>
        <span class="validity">Valid through ${escapeHtml(metadata.validity || 'not provided')}</span>
      </div>
      <details>
        <summary>View full traceability</summary>
        <div class="detail-content">
          <div><span>Service/API</span><code>${escapeHtml(metadata.service_or_api || 'Not provided')}</code></div>
          <div><span>Domain</span><p>${escapeHtml(module)}</p></div>
          <div><span>Suggested smoke test</span><p>Verify the primary flow described in this record using only its documented data.</p></div>
          <div><span>Source</span><p>QA Memory RAG fictional catalog</p></div>
        </div>
      </details>
      <div class="relevance" aria-label="Relevance ${relevance} percent">
        <div class="relevance-label"><span>Relevance</span><strong>${relevance}%</strong></div>
        <div class="relevance-track"><span style="width:${relevance}%"></span></div>
      </div>
    </article>`;
}

function render() {
  const item = data.find(sample => sample.case_id === select.value) || data[0];
  const chunks = item.chunks_related.map(renderChunk).join('');
  result.innerHTML = `
    <div class="result-head">
      <span class="badge">Evaluación ${escapeHtml(item.evaluation.score)}/10</span>
      <span class="case-id">${escapeHtml(item.case_id)}</span>
    </div>
    <h3>${escapeHtml(caseTranslations[item.case_id][0])}</h3>
    <p class="answer">${escapeHtml(caseTranslations[item.case_id][1])}</p>
    <div class="chunks">${chunks || '<p class="empty-state">No chunks retrieved: controlled abstention.</p>'}</div>`;
}

select.addEventListener('change', render);
render();
