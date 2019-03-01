import sys
import traceback

from vfrlight.config import config as cfg


class FieldChoice():
    '''
        this as a wrapper for all hardcoded values that needs to be set in
        our database as a choice constraint.
    '''

    def __init__(self, listOfChoices):
        self.listOfChoices = listOfChoices
        self.choices = [[x, x] for x in self.listOfChoices]
        self.max_length = max([len(item)
                               for item in self.listOfChoices])
        self.choices_dict = {x: x for x in listOfChoices}


# TODO thoses checks hoodies&sweatshirts","sweaters&cardigans are not found in fit
ProductTypeChoicesList = ["None", "dress", "top", "shirts", "vest", "blouse",
                          "pant", "short", "culott", "skirt",
                          "hoodies & sweatshirts", "sweaters & cardigans",
                          "t-shirts", "trousers", "jeans", "blazer",
                          "jumpsuits", "jacket", "coats", "pant", "trousers", "short", "jeans"
    , "skirt", "tops", "blouses", "tonics shirts", "t-shirts", "vests"
    , "hoodies and sweatshirts", "onesize", "jackets", "blazers", "light weight jackets"
    , "coats", "winter jackets", "jumpsuit", "fit and flare dress", "sheath dress", "shift dress", "shirt dress",
                          "crop top", "Pant", "Polo Shirts"]

FittingTypeChoicesList = ["None", "closefit", "fitted", "semi fitted", "semifit",
                          "loose fit", "oversized", "skinny", "close fit", "fitted", "slim",
                          "regular fit", "semi fitted", "relaxed fit", "loose fit", "oversized",
                          "tailored fit", "pencil skirt", "straight", "a-line", "pleated", "flared", "gathered",
                          "fitted bodice"
                          ]
'''
    here we define two possible values for fabric while
    the actual algorithm implementation needs value in the range [0,50]
    currently we are throwing random values [0,25] (- stretch and [25,50] (- nonestretch

    `(-`, it means belongs in mathmatical way
'''
fabricTypeChoicesList = ['stretch', 'nonestretch', 'knitted']
'''
    we could be more flexible when it comes to collection
    defined by admin on their stores, such flexiblity could be
    adapted when it comes to different language other than english
 '''
collection_gender_list = ["women", "men"]
# currently supported plans, where the third one is considered to be prime plan
PlanChoiceList = [primary + " " + key for primary in cfg.PLANS for key in
                  cfg.PLANS[primary]]  # eg: Male Free , Male First , MaleAndFemale First
'''
    when we are creating a new recurring charge to be confirmed by the admin
    the charge follow these states.
    first it gets in pending mode then if he confirms or declines
    it gets accepted/declined respectively, and finally once we have an
    accepted plan we could easily activated.
    please note that there is many scenarios I could clarify right here
     1) If Admin declines a charge nothing happens
     2) If Admin accepted some plan and we activated, and after that he
        wants to upgrade i.e (Male/Female)->(MaleAndFemale)
            or downgrade i.e (MaleAndFemale)->(Male/Female)
        we create new charge and we activate it if it gets accepted by the admin
        WHAT THAT MEANS?
            it means we don't cancel the previous charge explicitly, we let shopify
            handle that.
        OK BUT WHY?
            because if we cancel it by ourselves, it means the admin
            have to FULLY pay for the billing amount specified each month
            even if there is many days to the end of the month.
            BUT if shopify handle the cancel operation, then shopify calculate only
            how many days spent and charge him appropriately and the new charge will
            be set starting from the current date.

            see https://help.shopify.com/api/charging-for-your-app/faq

'''
plan_stausList = ['pending', 'accepted', 'active']

# defaultHeightMeasurementChoicesList = ["cm","inch"]
# defaultWeightMeasurementChoicesList = ["kg","pound"]

# instantiate field choice for all the lest above
productType = FieldChoice(ProductTypeChoicesList)
product_fit_Type = FieldChoice(FittingTypeChoicesList)
fabricType = FieldChoice(fabricTypeChoicesList)
plans = FieldChoice(PlanChoiceList)
plan_status = FieldChoice(plan_stausList)


# defaultHeightMeasurement = FieldChoice(defaultHeightMeasurementChoicesList)
# defaultWeightMeasurement = FieldChoice(defaultWeightMeasurementChoicesList)

def validate_variant_range(gender, body_part, value, Variant_Ranges,
                           metric, is_person=False):
    # As for profile, it's required to fill all additional values
    if not value:
        if is_person:
            return "{} is required".format(body_part)
        '''
            return None i.e no error has occured, please see how this method gets
            called and errors are accumulated accordingly
        '''
    return None

    print(metric)
    sys.stdout.flush()

    # if(not metric == 'cm'):
    #    value = in_to_cm(value)

    # Variant_Range = Variant_Ranges[gender]
    # (min_value, max_value) = (Variant_Range[0], Variant_Range[1])

    # if not (value >= min_value and value <= max_value):
    #     if(not metric == 'cm'):
    #         min_value, max_value = cm_to_in(min_value), cm_to_in(max_value)
    #     return (body_part + " value is not in the range [{},{}] for {}".format(
    #             min_value, max_value, gender))

    return None


class Variant_Ranges_dict:
    '''
        validation ranges for F:Female and M:Males
        notice that we unified the names for males and females
        such as seat for male is considered to be hips
        and chest is also bust, notice that all values are compared in cm metric
        so variable with inch is converted first then we apply this validation thing
    '''
    profile_ranges = {'bust': {'F': (0, 2000), 'M': (0, 2000)},
                      'waist': {'F': (0, 2000), 'M': (0, 2000)},
                      'hips': {'F': (0, 2000), 'M': (0, 2000)},
                      'shoulder': {'F': (0, 2000), 'M': (0, 2000)}, }

    product_ranges = {'bust': {'F': (0, 2000), 'M': (0, 2000)},
                      'waist': {'F': (0, 2000), 'M': (0, 2000)},
                      'hips': {'F': (0, 2000), 'M': (0, 2000)},
                      'shoulder': {'F': (0, 2000), 'M': (0, 2000)}, }


body_parts_list = ['shoulder', 'waist', 'hips', 'bust']
body_parts_choiceField = FieldChoice(body_parts_list)


def from_product_type_to_required_body_parts(variant_productType, gender):
    '''
        we design dictionary `switcher` to be more flexible once we have more
        product's type added in the future.
        it's used to impose a required_attributes constraint on variants of products
        since we have the product type we mostly need not all attributes to be filled
        by the merchant, i.e for jeans as a product type why do we have to fill shoulder measure
    '''

    bodyparts = {x: x for x in body_parts_list}
    switcher = {
        productType.choices_dict['hoodies and sweatshirts']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['sweaters & cardigans']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['tonics shirts']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['winter jackets']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['jackets']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['light weight jackets']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['blazers']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['vests']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['shirts']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['jeans']:
            [bodyparts['waist'], bodyparts['hips']],
        productType.choices_dict['trousers']:
            [bodyparts['waist'], bodyparts['hips']],
        productType.choices_dict['Pant']:
            [bodyparts['waist'], bodyparts['hips']],
        productType.choices_dict['short']:
            [bodyparts['waist'], bodyparts['hips']],
        productType.choices_dict['pant']:
            [bodyparts['waist'], bodyparts['hips']],
        productType.choices_dict['blazer']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['jacket']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['fit and flare dress']:
            [bodyparts['bust'], bodyparts['waist'],
             bodyparts['hips']],
        productType.choices_dict['sheath dress']:
            [bodyparts['bust'], bodyparts['waist'],
             bodyparts['hips']],
        productType.choices_dict['shift dress']:
            [bodyparts['bust'], bodyparts['waist'],
             bodyparts['hips']],
        productType.choices_dict['shirt dress']:
            [bodyparts['bust'], bodyparts['waist'],
             bodyparts['hips']],

        productType.choices_dict['blouses']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['jumpsuit']:
            [bodyparts['bust'], bodyparts['waist'],
             bodyparts['hips']],
        productType.choices_dict['top']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['tops']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['coats']:
            [bodyparts['bust'], bodyparts['waist']],

        productType.choices_dict['skirt']:
            [bodyparts['hips'], bodyparts['waist']],
        productType.choices_dict['t-shirts']:
            [bodyparts['bust'], bodyparts['waist']],
        # TODO: Jaber please check if only bust & waist are needed (I've only added them!!)
        productType.choices_dict['crop top']:
            [bodyparts['bust'], bodyparts['waist']],
        productType.choices_dict['Polo Shirts']:
            [bodyparts['bust'], bodyparts['waist']],

    }
    required_attributes = [bodyparts['hips'], bodyparts['waist'],
                           bodyparts['bust'], bodyparts['shoulder']]
    try:
        required_attributes = switcher[variant_productType]
    except Exception as e:
        traceback.format_exc()
    if (gender == 'F' and 'shoulder' in required_attributes):
        required_attributes.remove('shoulder')
    return required_attributes
