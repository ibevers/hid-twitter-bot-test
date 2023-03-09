





import sys
print()
print()
print(sys.path)




import sys
sys.path.insert(len(sys.path), 'backend/scripts')
from analyze import create_model_features as cmf
print(cmf.safe_division(1, 1))