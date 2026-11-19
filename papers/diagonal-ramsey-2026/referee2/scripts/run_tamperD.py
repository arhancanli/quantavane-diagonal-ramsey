import sys
sys.path.insert(0, 'research/tier2/ramsey-zbs/code/lemmaD')
import tamper_D
sys.exit(0 if tamper_D.main(sys.argv[1]) else 1)
