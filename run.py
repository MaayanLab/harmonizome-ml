#!/usr/bin/env python

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'preprocess':
        from app.preprocess import main
        main()
    else:
        from app.main import main
        main()
