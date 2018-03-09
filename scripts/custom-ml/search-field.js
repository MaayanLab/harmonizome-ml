// JS Deps: jquery, typeahead, bloodhound
// CSS Deps: search-field

// Modified from original Harmonizome
export function setupSearchField(searchEl) {
    let $searchEl = $(searchEl)
    let $typeaheadEl = $searchEl.find('input')

    function setupSearch() {
        let results = new Bloodhound({
            datumTokenizer: function (datum) {
                return Bloodhound.tokenizers.whitespace(datum.value)
            },
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: {
                url: $searchEl.attr('data') + '%QUERY',
                replace: function (url, urlEncodedQuery) {
                    url = url.replace('%QUERY', urlEncodedQuery)
                    return url
                },
                wildcard: '%QUERY'
            },
            limit: 20,
        })

        $typeaheadEl.typeahead(
                {
                    hint: true,
                    highlight: true,
                    minLength: 1,
                    limit: 20,
                },
                {
                    name: 'results',
                    source: results.ttAdapter(),
                    limit: 20,
                }
            )
        $searchEl
            .find('span.twitter-typeahead')
            .css('display', 'block')

        /* Now move the Typeahead suggestion box outside of the input
         * form. We do this because the input form needs
         * "overflow: hidden". See: http://jsfiddle.net/0z1uup9t/
         */
        monitorSuggestionsDropdown()
    }

    /* Setup Twitter Bootstrap JS tooltips.
     */
    function setupTooltips() {
        $searchEl.find('[data-toggle="tooltip"]').tooltip()
    }

    /* Correctly places the suggestion menu.
     */
    function placeSuggestionMenu() {
        let $ttMenu = $('.tt-menu'),
            $input = $searchEl.find('.input-bar')

        let offset = $input.offset()
        offset.top += $input.outerHeight()

        $ttMenu.css(offset).css('width', $input.width())
    }

    /* Handle correctly displaying Twitter Typeahead dropdown on any page.
     */
    function monitorSuggestionsDropdown() {
        $('.tt-menu').appendTo('body')
        // placeSuggestionMenu()
        // $(window).on('resize', placeSuggestionMenu)
        setOverlayWhenTyping()
    }

    /* Highlights user typing rather than screen contents.
     */
    function setOverlayWhenTyping() {
        let $input = $searchEl.find('.input-bar .tt-input')
        let inNav = $searchEl.hasClass('in-navbar')
        $input.keyup(function () {
            placeSuggestionMenu()
            var term = $input.val()
            if (term && inNav) {
                $searchEl.find('.wrapper').css('opacity', .1)
            } else {
                $searchEl.find('.wrapper').css('opacity', 1)
            }
        })
    }

    function setupHints() {
        let $input = $searchEl.find('.input-bar .tt-input')
        $searchEl.find('.hint').each(function() {
            let $hint = $(this)
            $hint.click(function() {
                $input.focus()
                $typeaheadEl.typeahead('val', $hint.text())
                $input.keyup()
            })
        })
    }

    setupSearch()
    setupTooltips()
    setupHints()
}
