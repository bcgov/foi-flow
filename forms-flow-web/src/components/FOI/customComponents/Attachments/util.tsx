import { AttachmentCategories } from '../../../../constants/FOI/statusEnum'

export const getCategory = (category: string) => {
  return AttachmentCategories.categorys.find(element => element.name === category) || AttachmentCategories.categorys.find(element => element.name === "general");
}