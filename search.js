// Simple client-side search that filters <article class="card"> elements
// Works on index.html and on each category index page

(function () {
    function initSearch() {
        var input = document.getElementById('site-search-input');
        if (!input) return; // no search box on this page

        var cards = Array.prototype.slice.call(document.querySelectorAll('article.card'));
        if (!cards.length) return;

        // optional "no results" message
        var noResults = document.getElementById('no-results-message');

        input.addEventListener('input', function () {
            var q = input.value.toLowerCase().trim();
            var visibleCount = 0;

            cards.forEach(function (card) {
                var text = card.innerText.toLowerCase();
                if (!q || text.indexOf(q) !== -1) {
                    card.style.display = '';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            if (noResults) {
                if (q && visibleCount === 0) {
                    noResults.style.display = 'block';
                } else {
                    noResults.style.display = 'none';
                }
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSearch);
    } else {
        initSearch();
    }
})();
