const applicationServerPublicKey = 'BPdu6l57dT6DadgVPmrau0iEDpMDgXE0hkcwOilU3MDdON4OWPnBVHeKaHBfLX2km8GTYHKlpcMj25nu4jdqdLs'

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').then(function(registration) {
    console.log('ServiceWorker registration successful with scope: ', registration.scope);
  }).catch(function(err) {
    console.log('ServiceWorker registration failed: ', err);
  });
}
