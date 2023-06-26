import foiFees from '../../../../constants/FOI/foiFees.json';
import type { CFRFormData, feeData } from './types';

export const calculateFees = (feeData: feeData) => {
  let k: keyof typeof feeData;
  let totalFee = 0;

  for (k in feeData) {
    totalFee += foiFees[k].type == "hour" ? calculateFeesByTime(k, feeData[k]) : calculateFeesByPages(k, feeData[k]);
  }

  return totalFee;
};

const calculateFeesByTime = (name: string, hours: number) => {
  if(hours <= 0) return 0;

  if(foiFees[name as keyof typeof foiFees]) {
    let feeItem : any = foiFees[name as keyof typeof foiFees];
    return (hours - feeItem["freehours"] <= 0) ? 0 : ((hours - feeItem["freehours"]) / feeItem["unit"]) * feeItem["price"];
  } else {
    return 0;
  }
}

const calculateFeesByPages = (name: string, pages: number) => {
  if(pages <= 0) return 0;

  if(foiFees[name as keyof typeof foiFees]) {
    let feeItem : any = foiFees[name as keyof typeof foiFees];
    return (pages / feeItem["unit"]) * feeItem["price"];
  } else {
    return 0;
  }
}

export const paymentMethods = [
  {
    value: 'init',
    label: 'Select Payment Method',
    disabled: true
  },
  {
    value: 'creditcardonline',
    label: 'Credit Card - Online',
    disabled: true,
  },
  {
    value: 'creditcardphone',
    label: 'Credit Card - Phone',
    disabled: false,
  },
  {
    value: 'cheque',
    label: 'Cheque',
    disabled: false,
  },
  {
    value: 'moneyorder',
    label: 'Money Order',
    disabled: false,
  },
  {
    value: 'cash',
    label: 'Cash',
    disabled: false,
  }
];