(() => {
if (document.documentElement.dataset.hubFrontendReady) return;
document.documentElement.dataset.hubFrontendReady = 'true';
function initializeNavigation() {
 const button = document.querySelector('[data-menu-toggle]');
 const menu = document.querySelector('#main-navigation');
 if (!button || !menu || button.dataset.initialized) return;
 button.dataset.initialized = 'true'; button.hidden = false;
 const close = () => { menu.classList.add('hidden'); button.setAttribute('aria-expanded', 'false'); };
 button.addEventListener('click', () => {
  const open = button.getAttribute('aria-expanded') !== 'true';
  button.setAttribute('aria-expanded', String(open)); menu.classList.toggle('hidden', !open);
 });
 menu.addEventListener('keydown', event => { if(event.key === 'Escape'){ close(); button.focus(); } });
 button.addEventListener('keydown', event => { if(event.key === 'Escape') close(); });
 close();
}
initializeNavigation();
document.addEventListener('htmx:load', initializeNavigation);
const showRequestError = () => document.querySelector('#request-error')?.removeAttribute('hidden');
document.addEventListener('htmx:responseError', showRequestError);
document.addEventListener('htmx:sendError', showRequestError);
document.addEventListener('htmx:beforeRequest', () => document.querySelector('#request-error')?.setAttribute('hidden', ''));

})();
