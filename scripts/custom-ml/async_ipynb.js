import { download } from './util'

function setupRemote(remote, request, callback) {
    let xhttp = new XMLHttpRequest()
    let response_index = 0
    xhttp.onreadystatechange = function() {
        if (this.status >= 400) {
            callback({
                type: 'status',
                value: 'Error: '+this.status,
            })
        } else {
            // Because responseText gets appended during this process,
            //  we save the last response_index of the string so that we can slice
            //  it and get the new text.
            var current = this.responseText.slice(response_index)
            // We split up all the lines processing them one at a time
            var updates = current.split('\n')
            while(updates.length > 1) {
                // Parse each line as JSON
                let current_update = JSON.parse(updates[0])
                callback(current_update)
                // Remove the parsed update moving the response_index forward
                response_index += updates[0].length + 1
                updates = updates.slice(1)
            }
        }
    }
    xhttp.open('POST', remote, true);
    // xhttp.setRequestHeader("Connection", "Keep-Alive");
    // xhttp.setRequestHeader('Content-type', 'multipart/form-data');
    xhttp.send(request);
}

export function setupRemoteIpynb(ipynb, params) {
    let $ipynb = $(ipynb)
    let $status = $($ipynb.attr('status'))
    let $savePredictions = $($ipynb.attr('savePredictions'))
    let $saveNotebook = $($ipynb.attr('saveNotebook'))
    let remote = $ipynb.attr('remote')
    let current_index
    let current_code_cell = 1
    let started = false
    let scroll = false
    params.append('filename', $ipynb.attr('filename'))
    
    setupRemote(
        remote,
        params,
        (update) => {
            console.log(update)
            if(update.type == 'progress') {
                let cell = $($ipynb.find('.cell')[update.value])
                let input_prompt =  $(cell.find('.input_prompt'))
                if(input_prompt.closest('.cell').hasClass('code_cell')) {
                    input_prompt.text('In [*]:')
                }
                let cell_output_status = $(cell.find('.output-status')[0])
                cell_output_status.removeClass('pending')
                cell_output_status.addClass('loading')

                current_index = update.value // save the current index
            } else if(update.type == 'status') {
                $status.text(update.value)
            } else if(update.type == 'error') {
                $status.text('Error: ' + update.value)
            } else if(update.type == 'cell') {
                if(update.value.cell_type == 'code') {
                    let cell = $($ipynb.find('.cell')[current_index])
                    let cell_output_subarea = cell.find('.output_subarea')
                    update.value.outputs.forEach((ele) => {
                        console.log(ele)
                        if(ele.output_type == 'stream') {
                            let cell_output_container = $('<div class="output_stream output_' + ele.name + ' output_text">')
                            let cell_output_text = $('<pre>').text(ele.text)
                            cell_output_container.append(cell_output_text)
                            cell_output_subarea.append(cell_output_container)
                        } else if(ele.output_type == 'execute_result') {
                            let cell_output_container = $('<div class="output_html rendered_html output_execute_result">')
                            let cell_output_html = ele.data['text/html']
                            cell_output_container.append(cell_output_html)
                            cell_output_subarea.append(cell_output_container)
                        } else if(ele.output_type == 'display_data') {
                            if(ele.data['image/png'] !== undefined) {
                                let cell_output_container = $('<div class="output_png">')
                                let cell_output_image = new Image()
                                cell_output_image.src = 'data:img/png;base64,' + ele.data['image/png']
                                cell_output_container.append(cell_output_image)
                                cell_output_subarea.append(cell_output_container)
                            } else if(ele.data['text/html'] !== undefined) {
                                let cell_output_container = $('<div class="output_html rendered_html output_execute_result">')
                                let cell_output_html = ele.data['text/html']
                                cell_output_container.append(cell_output_html)
                                cell_output_subarea.append(cell_output_container)
                            } else if(ele.data['text/plain'] !== undefined) {
                                let cell_output_container = $('<div class="output_stream output_' + ele.name + ' output_text">')
                                let cell_output_text = $('<pre>').text(ele.data['text/plain'])
                                cell_output_container.append(cell_output_text)
                                cell_output_subarea.append(cell_output_container)
                            } else {
                                console.warn("Unrecognized output type "+ele.output_type)
                            }
                        } else if(ele.output_type == 'error') {
                            let cell_output_container = $('<div class="output_subarea output_test output_error">')
                            let cell_output_text = $('<pre>').text(ele.ename+': '+ele.evalue+'\n'+ele.traceback)
                            cell_output_container.append(cell_output_text)
                            cell_output_subarea.append(cell_output_container)
                        } else {
                            console.warn("Unrecognized output type "+ele.output_type)
                        }
                    })
                    let cell_output_status = $(cell.find('.output-status')[0])
                    cell_output_status.removeClass('loading')
                    cell_output_status.addClass('ready')

                    let current_cell_ele = cell.find('.input_prompt')
                    current_cell_ele.text('In ['+(current_code_cell++)+']:')
                    if(scroll) {
                        $('html, body').animate({
                            scrollTop: current_cell_ele.offset().top
                        }, 2500)
                    }
                } else if(update.value.cell_type == 'markdown') {
                } else {
                    console.warn("Unrecognized cell type")
                }
            } else if(update.type == 'download') {
                $savePredictions.attr('disabled', false)
                $savePredictions.unbind()
                $savePredictions.click(function() {
                    download('predictions.csv', update.value)
                })
            } else if(update.type == 'notebook') {
                if(!started) {
                    $ipynb.html(update.value)
                    $ipynb.find('.cell.code_cell').each(function() {
                        let cell = $(this)

                        let cell_output_source_toggle = $('<div class="source-toggle">')
                        cell_output_source_toggle.click(function() {
                            if(cell.find('.input').css('display') == 'flex')
                                cell.find('.input').css('display', 'none')
                            else
                                cell.find('.input').css('display', 'flex')
                        })
                        cell.prepend(cell_output_source_toggle)

                        let cell_output_wrapper = $('<div class="output_wrapper">')
                        let cell_output = $('<div class="output">')
                        let cell_output_area = $('<div class="output_area">')
                        let cell_output_prompt = $('<div class="prompt">')
                        let cell_output_loading = $('<div class="output-status pending">')
                        cell_output_prompt.append(cell_output_loading)
                        cell_output_area.append(cell_output_prompt)
                        let cell_output_subarea = $('<div class="output_subarea">')
                        cell_output_area.append(cell_output_subarea)
                        cell_output.append(cell_output_area)
                        cell_output_wrapper.append(cell_output)
                        cell.append(cell_output_wrapper)
                    })
                    started = true;
                    $saveNotebook.attr('disabled', true)
                    $saveNotebook.unbind()
                    $savePredictions.attr('disabled', true)
                    $savePredictions.unbind()
                } else {
                    // Ensure all statuses are complete
                    $ipynb.find('.output-status.pending').each(function() {
                        let self = $(this)
                        self.removeClass('pending')
                        self.addClass('ready')
                    })
                    $saveNotebook.attr('disabled', false)
                    $saveNotebook.unbind()
                    $saveNotebook.click(function() {
                        download('output.ipynb', update.value)
                    })
                }
            }
        },
    )
}
