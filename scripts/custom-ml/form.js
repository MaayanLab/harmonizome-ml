// JS Deps: jquery
// CSS Deps: form
// form attrs: remote, filename

import { toObject } from './util'
import { setupSearchField } from './search-field'
import { setupRemoteIpynb } from './async_ipynb'

let animation_lock = false

function change_focus($form, $self, next) {
    if(animation_lock)
        return false
    animation_lock = true

    let current_fieldset = $self.parent()
    let next_fieldset = next ? current_fieldset.next() : current_fieldset.prev()
    let next_step_fn = next ? (now, mx) => {
        //as the opacity of current_fieldset reduces to 0 - stored in "now"
        //1. scale current_fieldset down to 80%
        let scale = 1 - (1 - now) * 0.2
        //2. bring next_fieldset from the right(50%)
        let left = (now * 50)+"%"
        //3. increase opacity of next_fieldset to 1 as it moves in
        let opacity = 1 - now
        current_fieldset.css({
            'transform': 'scale('+scale+')',
            'position': 'absolute'
        })
        next_fieldset.css({'left': left, 'opacity': opacity})
    } : (now, mx) => {
        //as the opacity of current_fieldset reduces to 0 - stored in "now"
        //1. scale next_fieldset from 80% to 100%
        let scale = 0.8 + (1 - now) * 0.2
        //2. take current_fieldset to the right(50%) - from 0%
        let left = ((1-now) * 50)+"%"
        //3. increase opacity of next_fieldset to 1 as it moves in
        let opacity = 1 - now
        current_fieldset.css({'left': left})
        next_fieldset.css({'transform': 'scale('+scale+')', 'opacity': opacity})
    }

    //activate next step on progressbar using the index of next_fieldset
    if(next)
        $form.find('.progressbar li').eq($('fieldset').index(next_fieldset)).addClass('active')
    else
        $form.find('.progressbar li').eq($('fieldset').index(current_fieldset)).removeClass('active')

    //show the next fieldset
    next_fieldset.show()

    //hide the current fieldset with style
    current_fieldset.animate({opacity: 0}, {
        step: next_step_fn,
        duration: 800, 
        complete: function(){
            current_fieldset.hide()
            animation_lock = false
        }, 
        //this comes from the custom easing plugin
        easing: 'easeInOutBack'
    })
}

function submitForm($form) {
    let context = toObject($form)
    let ipynb = $form.attr('ipynb')

    setupRemoteIpynb(ipynb, context)
}

export function setupForm(form) {
    let $form = $(form)
    
    $form.find('.search-field').each((ind, self) => {
        setupSearchField(self)
    })
    $form.find('.next').each((ind, self) => {
        let $self = $(self)
        $self.click(() => change_focus($form, $self, true))
    })
    $form.find('.previous').each((ind, self) => {
        let $self = $(self)
        $self.click(() => change_focus($form, $self, false))
    })
    $form.find('.submit').click(() => submitForm($form))
    $form.find('.select2').select2()
    $form.find('.spinner').each(function() {
        let $this = $(this)
        let $input = $this.find('input')
        let $buttons = $this.find('.btn')
        $($buttons[0]).click(function() {
            let max = $this.attr('max')
            $input.val(Math.min(max, Number($input.val()) + 1))
        })
        $($buttons[1]).click(function() {
            let min = $this.attr('min')
            $input.val(Math.max(min, Number($input.val()) - 1))
        })
    })
    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        let $target = $(e.target)
        let $tablist = $target.closest('ul[role="tablist"]')

        let type_field = $($tablist.attr('target'))
        let choice = $target.attr('target')

        type_field.val(choice)
    })
}
