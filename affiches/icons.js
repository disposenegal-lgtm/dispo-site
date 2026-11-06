// Remplace <i data-i="nom"></i> par l'icône SVG correspondante (trait, couleur = currentColor)
var P = {
 print:'<path d="M6 9V3h12v6M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2"/><rect x="6" y="14" width="12" height="7"/>',
 copy:'<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V5a2 2 0 00-2-2H5a2 2 0 00-2 2v9a2 2 0 002 2h3"/>',
 scan:'<path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2M3 12h18"/>',
 fax:'<rect x="2" y="8" width="20" height="13" rx="2"/><path d="M7 8V3h8l3 3v2M6 13h4M6 17h4M14 13h4v4h-4z"/>',
 speed:'<path d="M12 14l4-5"/><path d="M3.3 17a9 9 0 1117.4 0"/><circle cx="12" cy="14" r="1.5"/>',
 duplex:'<path d="M4 4h9l3 3v13H4z"/><path d="M17 10h3v11h-9v-1"/><path d="M8 12h4M8 15h4"/>',
 wifi:'<path d="M2 8.8a15 15 0 0120 0M5 12.6a10 10 0 0114 0M8.5 16.4a5 5 0 017 0"/><circle cx="12" cy="20" r="1"/>',
 lan:'<rect x="9" y="2" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="16" y="16" width="6" height="6" rx="1"/><path d="M12 8v4M5 16v-4h14v4"/>',
 usb:'<path d="M12 2v15M12 2l-2.5 3M12 2l2.5 3M7 9v3l5 3M17 7v4l-5 3"/><circle cx="12" cy="19" r="2.5"/><rect x="15.5" y="5" width="3" height="2"/><circle cx="7" cy="8" r="1.5"/>',
 touch:'<rect x="3" y="3" width="18" height="12" rx="2"/><path d="M10 21v-6.5a1.5 1.5 0 013 0V18l3 .5a1.5 1.5 0 011.2 1.7L17 22"/>',
 adf:'<path d="M5 3h10l4 4v14H5z"/><path d="M9 9h6M9 13h6M9 17h3"/>',
 mobile:'<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M11 18h2"/>',
 color:'<circle cx="8" cy="9" r="5"/><circle cx="16" cy="9" r="5"/><circle cx="12" cy="15.5" r="5"/>',
 phone:'<path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014.1 2h3a2 2 0 012 1.7c.1.9.4 1.8.7 2.7a2 2 0 01-.5 2.1L8 9.8a16 16 0 006 6l1.3-1.3a2 2 0 012.1-.5c.9.3 1.8.6 2.7.7a2 2 0 011.7 2z"/>',
 web:'<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 014 10 15 15 0 01-4 10 15 15 0 01-4-10 15 15 0 014-10z"/>',
 pin:'<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0116 0z"/><circle cx="12" cy="10" r="3"/>',
 shield:'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>'
};
document.querySelectorAll('i[data-i]').forEach(function (el) {
  el.outerHTML = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + P[el.dataset.i] + '</svg>';
});
