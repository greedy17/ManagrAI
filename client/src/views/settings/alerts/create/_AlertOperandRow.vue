<template>
  <div class="alert-operand-row">
    <!-- <span class="alert-operand-row--label">Alert Operands</span> -->

    <div style="margin-bottom: 2rem" class="centered" v-if="form.field.operandOrder.value != 0">
      <label class="alert-operand-row__condition-label">AND</label>
      <ToggleCheckBox
        @input="toggleSelectedCondition"
        :value="selectedCondition !== 'AND'"
        offColor="#199e54"
        onColor="#199e54"
      />
      <label class="alert-operand-row__condition-label">OR</label>
    </div>

    <div class="alert-operand-row__options">
      <div class="centered" style="flex-direction: column">
        <p style="font-weight: bold">Select CRM Field:</p>

        <!-- <CollectionSearch
          class="fields__height"
          :collection="objectFields"
          itemDisplayKey="referenceDisplayLabel"
          :showSubmitBtn="false"
          @onSearch="
            () => {
              formFields.pagination = new Pagination()
            }
          "
        >
          <template v-slot:item="{ result }">
            <div>
              <input
                id="key"
                :value="result.apiName"
                v-model="form.field.operandIdentifier.value"
                type="radio"
                @click="setIdentifier(result)"
              />
              <label for="result">{{ result['referenceDisplayLabel'] }}</label>
            </div>

            <div class="slack-form-builder__container">
                <CheckBox :checked="addedFieldIds.includes(result.id)" />
                <div class="slack-form-builder__sf-field">
                  {{ result['referenceDisplayLabel'] }}
                </div>
              </div>
          </template>
        </CollectionSearch> -->

        <FormField :errors="form.field.operandIdentifier.errors">
          <template v-slot:input>
            <DropDownSearch
              v-if="selectedOperandType == 'FIELD'"
              :items.sync="objectFields.list"
              :itemsRef.sync="form.field._operandIdentifier.value"
              v-model="form.field.operandIdentifier.value"
              displayKey="referenceDisplayLabel"
              valueKey="apiName"
              nullDisplay="Select Fields"
              searchable
              :hasNext="!!objectFields.pagination.hasNextPage"
              @load-more="objectFieldNextPage"
              @search-term="onSearchFields"
              @input="form.field.operandIdentifier.validate()"
            />
          </template>
        </FormField>
        <p
          @click="removeIdentifier"
          :class="form.field.operandIdentifier.value ? 'selected__item' : 'invisible'"
        >
          <img src="@/assets/images/remove.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          {{ form.field.operandIdentifier.value }}
        </p>
      </div>

      <div
        v-if="!(selectedFieldType == 'DATE' || selectedFieldType == 'DATETIME')"
        class="centered"
        style="flex-direction: column"
      >
        <p style="font-weight: bold">Select an operator:</p>
        <!-- <div :key="value" v-for="(key, value) in operatorOpts">
          <input
            v-model="form.field.operandOperator.value"
            id="key"
            :value="key.value"
            type="radio"
            @click="setOperator(key)"
          />
          <label for="key">{{ key.label }}</label>
        </div> -->
        <FormField :errors="form.field.operandOperator.errors">
          <template v-slot:input>
            <DropDownSearch
              :items.sync="operatorOpts"
              :itemsRef.sync="form.field._operandOperator.value"
              v-model="form.field.operandOperator.value"
              @input="form.field.operandOperator.validate()"
              displayKey="label"
              valueKey="value"
              nullDisplay="Select Operators"
              searchable
              local
            />
          </template>
        </FormField>
        <p
          @click="removeOperator"
          :class="form.field.operandOperator.value ? 'selected__item' : 'invisible'"
        >
          <img src="@/assets/images/remove.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          {{ form.field._operandOperator.value ? form.field._operandOperator.value.label : '' }}
        </p>
      </div>

      <div class="alert-operand-row__value">
        <div
          class="centered"
          style="flex-direction: column"
          v-if="selectedFieldTypeRaw == 'Picklist' && selectedFieldType == 'STRING'"
        >
          <p style="font-weight: bold">Select a value:</p>
          <!-- <div :key="value" v-for="(key, value) in picklistOpts">
            <input
              v-model="form.field.operandValue.value"
              id="key"
              :value="key.value"
              type="radio"
              @click="setOperand(key)"
            />
            <label for="key">{{ key.label }}</label>
          </div> -->

          <FormField :errors="form.field.operandValue.errors">
            <template v-slot:input>
              <DropDownSearch
                :items.sync="picklistOpts"
                :itemsRef.sync="form.field._operandValue.value"
                v-model="form.field.operandValue.value"
                displayKey="label"
                valueKey="value"
                nullDisplay="Select a value"
                searchable
                local
              />
            </template>
          </FormField>
          <p
            @click="removeValue"
            :class="form.field.operandValue.value ? 'selected__item' : 'invisible'"
          >
            <img
              src="@/assets/images/remove.png"
              style="height: 1rem; margin-right: 0.5rem"
              alt=""
            />
            {{ form.field.operandValue.value }}
          </p>
        </div>

        <template v-else>
          <div
            class="centered"
            style="flex-direction: column"
            v-if="selectedFieldType == 'BOOLEAN' && selectedFieldTypeRaw == 'Boolean'"
          >
            <p style="font-weight: bold">Select a value:</p>

            <FormField :errors="form.field.operandValue.errors">
              <template v-slot:input>
                <DropDownSearch
                  :items.sync="valueOpts"
                  :itemsRef.sync="form.field._operandValue.value"
                  v-model="form.field.operandValue.value"
                  displayKey="label"
                  valueKey="value"
                  nullDisplay="Select a value"
                  searchable
                  local
                />
              </template>
            </FormField>
            <p :class="form.field.operandValue.value ? 'selected__item' : ''">
              {{ form.field.operandValue.value }}
            </p>
          </div>

          <div v-else>
            <div
              style="
                display: flex;
                flex-direction: row;
                min-width: 34vw;
                justify-content: space-between;
                align-items: flex-start;
              "
              v-if="selectedFieldType == 'DATE' || selectedFieldType == 'DATETIME'"
            >
              <div style="text-align: center">
                <p style="font-weight: bold">Select an operator:</p>
                <!-- <div :key="value" v-for="(key, value) in operatorOpts">
                <input
                  v-model="form.field.operandOperator.value"
                  id="key"
                  :value="key.value"
                  type="radio"
                  @click="setOperator(key)"
                />
                <label for="key">{{ key.label }}</label>
                </div> -->
                <FormField :errors="form.field.operandOperator.errors">
                  <template v-slot:input>
                    <DropDownSearch
                      :items.sync="operatorOpts"
                      :itemsRef.sync="form.field._operandOperator.value"
                      v-model="form.field.operandOperator.value"
                      @input="form.field.operandOperator.validate()"
                      displayKey="label"
                      valueKey="value"
                      nullDisplay="Select Operators"
                      searchable
                      local
                    />
                  </template>
                </FormField>
                <p
                  style="margin-top: 2.25rem"
                  @click="removeOperator"
                  :class="form.field.operandOperator.value ? 'selected__item' : 'invisible'"
                >
                  <img
                    src="@/assets/images/remove.png"
                    style="height: 1rem; margin-right: 0.5rem"
                    alt=""
                  />
                  {{
                    form.field._operandOperator.value ? form.field._operandOperator.value.label : ''
                  }}
                </p>
              </div>

              <div>
                <div
                  class="centered"
                  style="margin-bottom: 0.8rem; margin-top: 0.75rem; margin-left: -1.5rem"
                >
                  <label class="alert-operand-row__condition-label">In the past</label>
                  <ToggleCheckBox
                    @input="toggleSelectedOperand"
                    :value="MyOperand !== 'Negative'"
                    offColor="#199e54"
                    onColor="#199e54"
                  />
                  <label class="alert-operand-row__condition-label">In the future</label>
                </div>

                <FormField v-if="MyOperand === 'Negative'" :errors="form.field.operandValue.errors">
                  <template v-slot:input>
                    <FormField
                      @blur="form.field.operandValue.validate()"
                      v-model="form.field.operandValue.value"
                      :inputType="getInputType(form.field._operandIdentifier.value)"
                      @input="
                        (e) => {
                          negVal(e)
                        }
                      "
                      placeholder="Number of days"
                    />
                  </template>
                </FormField>

                <FormField v-else :errors="form.field.operandValue.errors">
                  <template v-slot:input>
                    <FormField
                      @blur="form.field.operandValue.validate()"
                      v-model="form.field.operandValue.value"
                      :inputType="getInputType(form.field._operandIdentifier.value)"
                      placeholder="Number of days"
                    />
                  </template>
                </FormField>
                <p
                  style="margin-top: -0.5rem; width: 90%"
                  :class="form.field.operandValue.value ? 'selected__item' : 'invisible'"
                  @click="removeValue"
                >
                  <img
                    src="@/assets/images/remove.png"
                    style="height: 1rem; margin-right: 0.5rem"
                    alt=""
                  />
                  {{ form.field.operandValue.value }}
                </p>
              </div>

              <!-- <div style="display: flex; align-items: center">
                <p>{{ form.field.operandIdentifier.value }} is:</p>
                <div class="centered">
                  <label class="alert-operand-row__condition-label">In the past</label>
                  <ToggleCheckBox
                    @input="toggleSelectedOperand"
                    :value="MyOperand !== 'Negative'"
                    offColor="#199e54"
                    onColor="#199e54"
                  />
                  <label class="alert-operand-row__condition-label">In the Future</label>
                </div>
              </div>

              <div v-if="MyOperand === 'Negative'">
                <label for="quantityNeg">Number of <span>days</span>:</label>
                <input
                  id="quantityNeg"
                  name="quantityNeg"
                  v-model="form.field.operandValue.value"
                  type="number"
                  v-on:keyup="negVal(form.field.operandValue.value)"
                  class="dayInput"
                  @click="setIdentifier"
                />
              </div>

              <div v-else>
                <label for="quantity">Number of <span>days</span>:</label>
                <input
                  id="quantity"
                  name="quantity"
                  v-model="form.field.operandValue.value"
                  type="number"
                  class="dayInput"
                  @click="setIdentifier"
                />
              </div> -->
            </div>

            <div class="centered" style="flex-direction: column" v-else>
              <p style="font-weight: bold">Enter value:</p>
              <FormField
                @blur="form.field.operandValue.validate()"
                :errors="form.field.operandValue.errors"
                v-model="form.field.operandValue.value"
                :inputType="getInputType(form.field._operandIdentifier.value)"
                placeholder=""
              />
              <p :class="form.field.operandValue.value ? 'selected__item' : ''">
                {{ form.field.operandValue.value }}
              </p>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import ToggleCheckBox from '@thinknimble/togglecheckbox'

//Internal
import ListContainer from '@/components/ListContainer'
import FormField from '@/components/forms/FormField'
import DropDownSearch from '@/components/DropDownSearch'
/**
 * Services
 */
import { AlertOperandForm } from '@/services/alerts/'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import CollectionSearch from '@thinknimble/collection-search'
import {
  SObjectField,
  SObjectValidations,
  SObjectPicklist,
  NON_FIELD_ALERT_OPTS,
} from '@/services/salesforce'
import {
  ALERT_DATA_TYPE_MAP,
  INPUT_TYPE_MAP,
  INTEGER,
  STRING,
  DATE,
  DECIMAL,
  BOOLEAN,
  DATETIME,
} from '@/services/salesforce/models'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertOperandRow',
  components: { ListContainer, ToggleCheckBox, DropDownSearch, FormField, CollectionSearch },
  props: {
    form: { type: AlertOperandForm },
    resourceType: { type: String },
  },
  data() {
    return {
      objectFields: CollectionManager.create({
        ModelClass: SObjectField,
        filters: { forAlerts: true, filterable: true, page: 1 },
      }),
      // used by dropdown as a ref field to retrieve obj of selected opt
      selectedOperandFieldRef: null,
      // used by dd as a ref field to retrieve obj of selected opt
      selectedOperandValueRef: null,
      picklistOpts: [],
      operandDate: '',
      NON_FIELD_ALERT_OPTS,
      negativeOperand: false,
      positiveOperand: false,
      MyOperand: 'Negative',
      intOpts: [
        { label: 'Greater or equal to', value: '>=' },
        { label: 'Greater than', value: '>' },
        { label: 'Less or equal to', value: '<=' },
        { label: 'Less than', value: '<' },
        { label: 'Equal to', value: '=' },
        { label: 'Not equal to', value: '!=' },
        // string based equality
      ],
      strOpts: [
        // string based equality
        { label: 'Contains', value: 'CONTAINS' },
        { label: 'Starts With', value: 'STARTSWITH' },
        { label: 'Ends With', value: 'ENDSWITH' },
        { label: '= (Equals)', value: '=' },
        { label: '!= (Not Equals)', value: '!=' },
      ],
      dateValueOpts: [
        { label: 'Same Day as alert day', value: '0' },
        { label: '7 days FROM alert day', value: '7' },
        { label: '7 days PRIOR TO alert day', value: '-7' },
        { label: '15 Days FROM alert day', value: '15' },
        { label: '15 Days PRIOR TO alert day', value: '-15' },
        { label: 'Month  FROM alert day', value: '30' },
        { label: 'Month  PRIOR TO alert day', value: '-30' },
      ],
      NegativeDateValues: [
        { label: 'Day of alert', value: '0' },
        { label: 'A month before', value: '-30' },
        { label: "Two month's before", value: '-60' },
        { label: "Three month's before", value: '-90' },
        { label: 'A week before', value: '-7' },
        { label: "Two week's before", value: '-14' },
        { label: '1 day before', value: '-1' },
        { label: "2 day's before", value: '-2' },
        { label: "3 day's before", value: '-3' },
        { label: "4 day's before", value: '-4' },
        { label: "5 day's before", value: '-5' },
        { label: "6 day's before", value: '-6' },
        { label: "7 day's before", value: '-7' },
        { label: "8 day's before", value: '-8' },
        { label: "9 day's before", value: '-9' },
        { label: "10 day's before", value: '-10' },
        { label: "11 day's before", value: '-11' },
        { label: "12 day's before", value: '-12' },
        { label: "13 day's before", value: '-13' },
        { label: "14 day's before", value: '-14' },
        { label: "15 day's before", value: '-15' },
        { label: "16 day's before", value: '-16' },
        { label: "17 day's before", value: '-17' },
        { label: "18 day's before", value: '-18' },
        { label: "19 day's before", value: '-19' },
        { label: "20 day's before", value: '-20' },
        { label: "21 day's before", value: '-21' },
        { label: "22 day's before", value: '-22' },
        { label: "23 day's before", value: '-23' },
        { label: "24 day's before", value: '-24' },
        { label: "25 day's before", value: '-25' },
        { label: "26 day's before", value: '-26' },
        { label: "27 day's before", value: '-27' },
        { label: "28 day's before", value: '-28' },
        { label: "29 day's before", value: '-29' },
      ],
      PositiveDateValues: [
        { label: 'Day of alert', value: '0' },
        { label: 'A month away', value: '30' },
        { label: "Two month's away", value: '60' },
        { label: "Three month's away", value: '90' },
        { label: 'A week away', value: '7' },
        { label: "Two week's away", value: '14' },
        { label: '1 day away', value: '1' },
        { label: "2 day's away", value: '2' },
        { label: "3 day's away", value: '3' },
        { label: "4 day's away", value: '4' },
        { label: "5 day's away", value: '5' },
        { label: "6 day's away", value: '6' },
        { label: "7 day's away", value: '7' },
        { label: "8 day's away", value: '8' },
        { label: "9 day's away", value: '9' },
        { label: "10 day's away", value: '10' },
        { label: "11 day's away", value: '11' },
        { label: "12 day's away", value: '12' },
        { label: "13 day's away", value: '13' },
        { label: "14 day's away", value: '14' },
        { label: "15 day's away", value: '15' },
        { label: "16 day's away", value: '16' },
        { label: "17 day's away", value: '17' },
        { label: "18 day's away", value: '18' },
        { label: "19 day's away", value: '19' },
        { label: "20 day's away", value: '20' },
        { label: "21 day's away", value: '21' },
        { label: "22 day's away", value: '22' },
        { label: "23 day's away", value: '23' },
        { label: "24 day's away", value: '24' },
        { label: "25 day's away", value: '25' },
        { label: "26 day's away", value: '26' },
        { label: "27 day's away", value: '27' },
        { label: "28 day's away", value: '28' },
        { label: "29 day's away", value: '29' },
      ],
      booleanValueOpts: [
        { label: 'True', value: 'true' },
        { label: 'False', value: 'false' },
      ],
    }
  },
  watch: {
    selectedFieldRef: {
      immediate: true,
      deep: true,
      async handler(val) {
        if (val && val.apiName && val.dataType == 'Picklist') {
          await this.listPicklists({ picklistFor: val.apiName })
        }
      },
    },
    resourceType: {
      async handler(val) {
        this.objectFields.filters = {
          ...this.objectFields.filters,
          forAlerts: true,
          filterable: true,
          salesforceObject: val,
        }
        this.objectFields.refresh()
      },
    },
  },
  async created() {
    this.objectFields.filters = {
      ...this.objectFields.filters,
      salesforceObject: this.resourceType,
    }
    await this.objectFields.refresh()
  },
  methods: {
    removeIdentifier() {
      this.form.field.operandIdentifier.value = ''
    },
    removeOperator() {
      this.form.field.operandOperator.value = ''
    },
    removeValue() {
      this.form.field.operandValue.value = ''
    },
    getInputType(type) {
      if (type && INPUT_TYPE_MAP[type.dataType]) {
        return INPUT_TYPE_MAP[type.dataType]
      }
      return 'text'
    },
    setIdentifier() {
      if (this.selectedFieldType == 'DATE' || this.selectedFieldType == 'DATETIME') {
        this.form.field.operandOperator.value = '<='
        this.form.field._operandOperator.value = { label: '<= (Less or Equal)', value: '<=' }
      }
    },
    setOperator(obj) {
      this.form.field._operandOperator.value = obj
    },
    setOperand(obj) {
      this.form.field._operandValue.value = obj
    },
    toggleSelectedCondition() {
      this.selectedCondition == 'AND'
        ? (this.selectedCondition = 'OR')
        : (this.selectedCondition = 'AND')
    },
    toggleSelectedOperand() {
      this.form.field.operandValue.value = ''
      this.MyOperand === 'Negative' ? (this.MyOperand = 'Positive') : (this.MyOperand = 'Negative')
    },
    async objectFieldNextPage() {
      await this.objectFields.addNextPage()
    },
    async onSearchFields(v) {
      this.objectFields.pagination = new Pagination()
      this.objectFields.filters = {
        ...this.objectFields.filters,
        search: v,
      }
      await this.objectFields.refresh()
    },
    async listPicklists(query_params = {}) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)

        this.picklistOpts = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    negVal(val) {
      if (val <= 0) {
        val = val
      } else {
        val = val * -1
      }
      val < 0
        ? (this.form.field.operandValue.value = -Math.abs(val).toString())
        : (this.form.field.operandValue.value = '0')
      console.log(this.form.field.operandValue.value)
    },
  },
  computed: {
    selectedField() {
      return this.form.field.operandIdentifier.value
    },

    selectedFieldTypeRaw() {
      if (this.form.field._operandIdentifier.value) {
        return this.form.field._operandIdentifier.value.dataType
      }
      return null
    },
    selectedFieldRef() {
      if (this.selectedFieldTypeRaw) {
        return this.form.field._operandIdentifier.value
      }
      return null
    },
    selectedFieldType() {
      if (this.selectedFieldTypeRaw) {
        return ALERT_DATA_TYPE_MAP[this.form.field._operandIdentifier.value.dataType]
      } else {
        return STRING
      }
    },
    operatorOpts() {
      switch (this.selectedFieldType) {
        case INTEGER:
          return this.intOpts
        case DECIMAL:
          return this.intOpts
        case DATE:
          return this.intOpts
        case DATETIME:
          return this.intOpts
        default:
          return this.strOpts
      }
    },
    valueOpts() {
      if (this.selectedFieldType) {
        if (this.selectedFieldType == DATE || this.selectedFieldType == DATETIME) {
          return this.dateValueOpts
        } else {
          return this.booleanValueOpts
        }
      }
      return this.booleanValueOpts
    },
    selectedCondition: {
      get() {
        return this.form.field.operandCondition.value
      },
      set(val) {
        this.form.field.operandCondition.value = val
      },
    },
    selectedOperandType: {
      get() {
        return this.form.field.operandType.value
      },
      set(val) {
        this.form.field.operandType.value = val
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/buttons';

::v-deep .input-content {
  width: 6rem;
  background-color: white;
}
::v-deep .input-form {
  width: 6rem;
  box-shadow: 3px 4px 7px $very-light-gray;
}
img {
  filter: invert(90%);
}
::v-deep .collection-search .collection-search__form .collection-search__input .search__input {
  font-family: Lato-Regular, sans-serif;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  font-size: 16px;
  border-radius: 4px;
  padding: 3%;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: $panther;
  height: 2.5rem;
  background-color: white;
  border: 1px solid #5d5e5e;
  width: 10rem;
  padding: 0 0 0 1rem;
  margin: 1rem;
  -webkit-box-shadow: 1px 4px 7px black;
  box-shadow: 1px 4px 7px black;
}
::v-deep .collection-search__result-item {
  overflow: auto;
  padding: 0 0.5rem;
  border: none;
}
::v-deep .collection-search__result-item:hover {
  background-color: transparent;
}
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
}
.btn {
  &--danger {
    @include button-danger();
  }
  &--primary {
    @include primary-button();
  }
  &--secondary {
    @include secondary-button();
  }

  &--icon {
    @include --icon();
  }
}
.dayInput {
  width: 50px;
  margin-left: 0.25rem;
  border-radius: 0.25rem;
}
.alert-operand-row {
  // @include standard-border();
  // margin: 1rem;
  // padding: 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  &--label {
    top: -1.05rem;
    position: relative;
    @include muted-font();
  }
}
.alert-operand-row__condition {
  position: relative;
  top: 0rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  &-label {
    margin: 0 0.5rem;
    font-size: 15px;
    font-weight: bold;
  }
}
.alert-operand-row__date-range {
  // displays a message on top of the input field for date/datetime selection
  position: absolute;
  display: flex;
  flex-direction: column;
  width: 15rem;
  margin-left: 2rem;
  @include muted-font(14px);
}
.alert-operand-row__options {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  justify-content: space-evenly;
  margin-top: -1rem;
  &-label {
    color: black;
  }
}
.fields__height {
  height: 26vh;
  overflow-y: scroll;
}
.toggle__row {
  display: flex;
  flex-direction: row;
}
.mar {
  margin-top: 1rem;
}
.column {
  display: flex;
  flex-direction: column;
  margin: 1rem;
}
.row {
  display: flex;
  flex-direction: row;
  margin: 0.2rem;
}
::-webkit-scrollbar {
  background-color: $panther;
  -webkit-appearance: none;
  width: 4px;
  height: 100%;
}
::-webkit-scrollbar-thumb {
  border-radius: 2px;
  background-color: $panther-silver;
}
.selected__item {
  padding: 0.5rem;

  box-shadow: 3px 4px 7px $very-light-gray;
  border-radius: 0.3rem;
  width: 100%;
  text-align: center;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}
.invisible {
  display: none;
}
</style>