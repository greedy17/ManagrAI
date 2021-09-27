<template>
  <div class="alert-operand-row">
    <!-- <span class="alert-operand-row--label">Alert Operands</span> -->

    <div class="centered" v-if="form.field.operandOrder.value != 0">
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
      <div style="margin: 0 0.3rem">
        <p style="color: #beb5cc">Search/Select SFDC field:</p>
        <CollectionSearch
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

            <!-- <div class="slack-form-builder__container">
                <CheckBox :checked="addedFieldIds.includes(result.id)" />
                <div class="slack-form-builder__sf-field">
                  {{ result['referenceDisplayLabel'] }}
                </div>
              </div> -->
          </template>
        </CollectionSearch>

        <!-- <FormField :errors="form.field.operandIdentifier.errors">
          <template v-slot:input>
            <DropDownSearch
              v-if="selectedOperandType == 'FIELD'"
              :items="objectFields.list"
              :itemsRef.sync="form.field._operandIdentifier.value"
              v-model="form.field.operandIdentifier.value"
              displayKey="referenceDisplayLabel"
              valueKey="apiName"
              nullDisplay="Search SFDC fields"
              searchable
              :hasNext="!!objectFields.pagination.hasNextPage"
              @load-more="objectFieldNextPage"
              @search-term="onSearchFields"
              @input="form.field.operandIdentifier.validate()"
            />
          </template>
        </FormField> -->
      </div>
      <div
        v-if="!(selectedFieldType == 'DATE' || selectedFieldType == 'DATETIME')"
        class="alert-operand-row__operator"
        style="margin: 0 0.3rem"
      >
        <p style="color: #beb5cc">Select an operator:</p>
        <div :key="value" v-for="(key, value) in operatorOpts">
          <input
            v-model="form.field.operandOperator.value"
            id="key"
            :value="key.value"
            type="radio"
            @click="setOperator(key)"
          />
          <label for="key">{{ key.label }}</label>
        </div>
        <!-- <FormField :errors="form.field.operandOperator.errors">
          <template v-slot:input>
            <DropDownSearch
              :items.sync="operatorOpts"
              :itemsRef.sync="form.field._operandOperator.value"
              v-model="form.field.operandOperator.value"
              @input="form.field.operandOperator.validate()"
              displayKey="label"
              valueKey="value"
              nullDisplay="Select an Operator"
              searchable
              local
            />
          </template>
        </FormField> -->
      </div>
      <div class="alert-operand-row__value">
        <div v-if="selectedFieldTypeRaw == 'Picklist' && selectedFieldType == 'STRING'">
          <p style="color: #beb5cc">Select a value:</p>
          <div :key="value" v-for="(key, value) in picklistOpts">
            <input
              v-model="form.field.operandValue.value"
              id="key"
              :value="key.value"
              type="radio"
              @click="setOperand(key)"
            />
            <label for="key">{{ key.label }}</label>
          </div>
        </div>
        <!-- <FormField :errors="form.field.operandValue.errors">
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
        </FormField> -->
        <template v-else>
          <div v-if="selectedFieldType == 'BOOLEAN' && selectedFieldTypeRaw == 'Boolean'">
            <p style="color: #beb5cc">Select a value:</p>
            <div :key="value" v-for="(key, value) in valueOpts">
              <input
                v-model="form.field.operandValue.value"
                id="key"
                :value="key.value"
                type="radio"
                @click="setOperand(key)"
              />
              <label for="key">{{ key.label }}</label>
            </div>
          </div>
          <!-- <FormField
            
            :errors="form.field.operandValue.errors"
          >
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
          </FormField> -->
          <div v-else>
            <div v-if="selectedFieldType == 'DATE' || selectedFieldType == 'DATETIME'">
              <div style="display: flex; align-items: center">
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
                />
              </div>
            </div>

            <div v-else>
              <p style="color: #beb5cc">Enter value:</p>
              <FormField
                @blur="form.field.operandValue.validate()"
                :errors="form.field.operandValue.errors"
                v-model="form.field.operandValue.value"
                :inputType="getInputType(form.field._operandIdentifier.value)"
                placeholder=""
              />
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
        { label: '>= (Greater or Equal)', value: '>=' },
        { label: '<= (Less or Equal)', value: '<=' },
        { label: '< (Less)', value: '<' },
        { label: '> (Greater)', value: '>' },
        { label: '= (Equals)', value: '=' },
        { label: '!= (Not Equals)', value: '!=' },
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
    getInputType(type) {
      if (type && INPUT_TYPE_MAP[type.dataType]) {
        return INPUT_TYPE_MAP[type.dataType]
      }
      return 'text'
    },
    setIdentifier(obj) {
      this.form.field._operandIdentifier.value = obj
      if (this.selectedFieldType == 'DATE' || this.selectedFieldType == 'DATETIME') {
        this.form.field.operandOperator.value = '='
        this.form.field._operandOperator.value = { label: '= (Equals)', value: '=' }
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
      this.form.field.operandValue.value = '0'
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
      let newVal = ''
      if (val < 0) {
        val = val
      } else {
        val = val * -1
      }
      newVal = -Math.abs(val).toString()
      this.form.field.operandValue.value = newVal
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
  background-color: $panther-silver;
}
::v-deep .input-form {
  width: 6rem;
}

::v-deep .collection-search .collection-search__form .collection-search__input .search__input {
  font-family: Lato-Regular, sans-serif;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  font-size: 16px;
  border-radius: 4px;
  background-color: #ffffff;
  padding: 3%;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: #4d4e4c;
  height: 2.5rem;
  background-color: #beb5cc;
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
    @include muted-font();
    margin: 0 0.5rem;
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
</style>
