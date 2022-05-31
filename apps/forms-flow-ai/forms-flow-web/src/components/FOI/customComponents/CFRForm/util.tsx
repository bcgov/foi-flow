import foiFees from '../../../../constants/FOI/foiFees.json';
import type { CFRFormData } from './types';

export const calculateFees = (cfrForm: CFRFormData) => {
  let k: keyof typeof cfrForm.estimates;
  let totalFee = 0;

  console.log("calculateFees");
  console.log(foiFees);
  // console.log(cfrForm);
  // console.log(cfrForm.estimates);

  for (k in cfrForm.estimates) {
    let value = cfrForm.actual && cfrForm.actual[k] && cfrForm.actual[k] > 0 ? cfrForm.actual[k] : cfrForm.estimates[k];
    totalFee += foiFees[k].type == "hour" ? calculateFeesByTime(k, value) : calculateFeesByPages(k, value);
  }

  cfrForm.amountDue = totalFee;

  return cfrForm;
};

const calculateFeesByTime = (name: string, hours: number) => {
  console.log("calculateFeesByTime");
  console.log(name);
  console.log(hours);

  if(hours <= 0) return 0;

  if(foiFees[name as keyof typeof foiFees]) {
    let feeItem : any = foiFees[name as keyof typeof foiFees];
    console.log(feeItem);
    return (hours - feeItem["freehours"] <= 0) ? 0 : ((hours - feeItem["freehours"]) / feeItem["unit"]) * feeItem["price"];
  } else {
    return 0;
  }
}

const calculateFeesByPages = (name: string, pages: number) => {
  console.log("calculateFeesByPages");
  console.log(name);
  console.log(pages);

  if(pages <= 0) return 0;

  if(foiFees[name as keyof typeof foiFees]) {
    let feeItem : any = foiFees[name as keyof typeof foiFees];
    console.log(feeItem);
    return (pages / feeItem["unit"]) * feeItem["price"];
  } else {
    return 0;
  }
}