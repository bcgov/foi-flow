import foiFees from '../../../../constants/FOI/foiFees.json';
import type { CFRFormData } from './types';

export const calculateFees = (cfrForm: CFRFormData) => {
  let newObj : any = {...cfrForm.estimates, ...cfrForm.actual};
  let k: keyof typeof newObj;
  let newFoiFees : any = foiFees;
  let totalFee = 0;

  for (k in newObj) {
    totalFee += newFoiFees[k]["type"] == "hour" ? calculateFeesByTime(k, newObj[k]) : calculateFeesByPages(k, newObj[k]);
  }

  cfrForm.amountDue = totalFee;

  return cfrForm;
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