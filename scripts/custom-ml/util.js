// JSDeps: jquery

export function download(filename, text) {
    let element = document.createElement('a')
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text))
    element.setAttribute('download', filename)

    element.style.display = 'none'
    document.body.appendChild(element)

    element.click()

    document.body.removeChild(element)
}

export function toObject(form) {
    return $(form).serializeArray().reduce((acc, val) => {
        if(acc[val.name] !== undefined) {
            if(typeof acc[val.name] !== 'object') {
                acc[val.name] = [acc[val.name]]
            }
            acc[val.name].push(val.value)
        } else {
            acc[val.name] = val.value
        }
        return acc
    }, {})
}
