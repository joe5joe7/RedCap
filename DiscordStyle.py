def style(input, style = 'blue' ):
    init = ''
    pre = ''
    post = ''
    close = ''

    #Configure style variables depending on input
    if style == 'blue':
        init = '```ini\n'
        pre = '['
        post = ']\n'
        close = '```'
    elif style == 'red':
        init = '```diff\n'
        pre = '- '
        post = '\n'
        close = '```'
    else:
        print('style not found' + style)

    #format the input according to style variables
    result = init
    preConversion = input.splitlines()
    for line in preConversion:
        result = result + (pre + line + post)
    return (result + close)
