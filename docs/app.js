const data = window.QA_MEMORY_SAMPLES.samples;
const select = document.querySelector('#case-select');
const result = document.querySelector('#result');

for (const sample of data) {
  const option = document.createElement('option');
  option.value = sample.case_id;
  option.textContent = `${sample.case_id} · ${sample.user_question}`;
  select.append(option);
}

const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
}[char]));

const splitIds = value => String(value || '').split(',').map(id => id.trim()).filter(Boolean);

function getSummary(chunk) {
  const title = chunk.metadata?.title || '';
  const prefix = `${chunk.id} | ${chunk.type} | módulo ${chunk.module}. ${title}.`;
  return chunk.content.startsWith(prefix) ? chunk.content.slice(prefix.length).trim() : chunk.content;
}

function renderRelations(relatedIds) {
  const ids = splitIds(relatedIds);
  if (!ids.length) return '<span class="empty-value">Sin relaciones registradas</span>';
  return ids.map(id => `<span class="id-chip">${escapeHtml(id)}</span>`).join('');
}

function renderChunk(chunk) {
  const metadata = chunk.metadata || {};
  const isBug = chunk.type === 'bug';
  const relevance = Math.round(Number(chunk.score) * 100);
  const typeLabel = isBug ? 'Bug' : 'Test case';

  return `
    <article class="chunk chunk--${isBug ? 'bug' : 'test'}">
      <div class="chunk-head">
        <span class="chunk-id">${escapeHtml(chunk.id)}</span>
        <span class="type-badge">${typeLabel}</span>
      </div>
      <h4>${escapeHtml(metadata.title || chunk.id)}</h4>
      <p class="chunk-summary">${escapeHtml(getSummary(chunk))}</p>
      <dl class="facts">
        <div><dt>Módulo</dt><dd>${escapeHtml(chunk.module)}</dd></div>
        <div><dt>Operación</dt><dd><code>${escapeHtml(metadata.endpoint_or_operation || 'No informada')}</code></dd></div>
        <div><dt>Owner</dt><dd>${escapeHtml(metadata.owner_team || 'No informado')}</dd></div>
        <div><dt>Relaciones</dt><dd class="relations">${renderRelations(metadata.related_ids)}</dd></div>
      </dl>
      <div class="evidence-row">
        <span class="evidence-badge">● Evidencia ${escapeHtml(metadata.evidence_state || 'desconocida')}</span>
        <span class="validity">Vigencia ${escapeHtml(metadata.validity || 'no informada')}</span>
      </div>
      <details>
        <summary>Ver trazabilidad completa</summary>
        <div class="detail-content">
          <div><span>Servicio/API</span><code>${escapeHtml(metadata.service_or_api || 'No informado')}</code></div>
          <div><span>Dominio</span><p>${escapeHtml(metadata.functional_domain || 'No informado')}</p></div>
          <div><span>Smoke sugerido</span><p>${escapeHtml(metadata.suggested_smoke || 'No informado')}</p></div>
          <div><span>Fuente</span><p>${escapeHtml(metadata.source || 'No informada')}</p></div>
        </div>
      </details>
      <div class="relevance" aria-label="Relevancia ${relevance} por ciento">
        <div class="relevance-label"><span>Relevancia</span><strong>${relevance}%</strong></div>
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
    <h3>${escapeHtml(item.user_question)}</h3>
    <p class="answer">${escapeHtml(item.system_answer)}</p>
    <div class="chunks">${chunks || '<p class="empty-state">Sin chunks: abstención controlada.</p>'}</div>`;
}

select.addEventListener('change', render);
render();
