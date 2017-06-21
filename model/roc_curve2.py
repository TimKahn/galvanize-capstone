import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import auc, roc_auc_score, roc_curve, precision_recall_curve
from scipy import interp
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from imblearn.combine import SMOTETomek, SMOTEENN
from imblearn.over_sampling import SMOTE
# from imblearn.under_sampling import TomekLinks, AllKNN

def plot_ROC_curve(classifiers, X, y, balancing=[], pos_label=1, n_folds=5):
    '''
    Input:
    -classifiers is a list of sklearn classifier objects
    -balancing is a list of sklearn over- and undersampling techniques
    Output:
    -a single plot with ROC curves for all balancing-classifier combinations
    '''
    print(balancing)
    if len(balancing) > 0:
        print('Preprocessing...')
        for cl in classifiers:
                for b in balancing:
                    mean_tpr, mean_fpr, mean_auc = get_ROC_curve(cl, X, y, b)
                    plt.plot(mean_fpr, mean_tpr, label=cl.__class__.__name__ + ' (AUC = %0.3f)' % mean_auc, lw=2)
    else:
        for cl in classifiers:
            mean_tpr, mean_fpr, mean_auc = get_ROC_curve(cl, X, y)
            plt.plot(mean_fpr, mean_tpr, label=cl.__class__.__name__ + ' (AUC = %0.3f)' % mean_auc, lw=2)

    plt.plot([0, 1], [0, 1], '--', color='black', label='Random')
    plt.axvline(x=50*y.sum()/len(y), label='50:1 FP/TP ratio', color='grey') # FPR such that FP:TP = 30:1
    # plt.axhline(y=.6, color='grey')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('FPR, n = 76,601')
    plt.ylabel('TPR, n = 92')
    # plt.title('ROC curve')
    plt.legend(loc="lower right")
    plt.show()

def get_ROC_curve(classifier, X, y, balancing=None, pos_label=1, n_folds=5):
    '''
    Called by plot_ROC_curve.  Outputs mean ROC curve and mean AUC from n-fold validation
    on the balancing-classifier pair.
    '''
    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    all_tpr = []
    skf = StratifiedKFold(n_splits=n_folds, random_state=40, shuffle=True)
    i = 1
    for train, test in skf.split(X, y):
        X_train, y_train = X[train], y[train]
        if balancing:
            X_train, y_train = balancing.fit_sample(X_train, y_train)
        classifier.fit(X_train, y_train)
        probas_ = classifier.predict_proba(X[test])
        fpr, tpr, thresholds = roc_curve(y[test], probas_[:, 1], pos_label=1)
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        roc_auc = auc(fpr, tpr)
        print(roc_auc)
        # plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))
        i += 1
    mean_tpr /= n_folds
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    return mean_tpr, mean_fpr, mean_auc

def plot_PR_curve(classifier, X, y, n_folds=5):
    '''
    Plots the average precision-recall curve for a classifier over n-fold cross validation.
    '''
    skf = StratifiedKFold(n_splits=n_folds, random_state=40, shuffle=True)
    i = 1
    for train, test in skf.split(X, y):
        classifier.fit(X[train], y[train])
        probas_ = classifier.predict_proba(X[test])
        precision, recall, thresholds = precision_recall_curve(y[test], probas_[:,1], pos_label=1)
        plt.plot(recall, precision, lw=1, label='PR fold %d' % (i,))
        i += 1
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-recall curve')
    plt.legend(loc="lower right")
    plt.show()

if __name__ == '__main__':
    print('Please import this script to call its functions.')
