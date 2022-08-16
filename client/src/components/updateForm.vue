<template>
  <div>
    <Modal dimmed>
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="
                height: 1.75rem;
                margin-left: 0.5rem;
                margin-right: 0.25rem;
                filter: brightness(120%);
              "
              alt=""
            />
            <h3>Update {{ resource }}</h3>
          </div>
          <img
            src="@/assets/images/close.svg"
            style="height: 1.5rem; margin-top: -1rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetEdit"
            alt=""
          />
        </div>
        <div class="opp-modal">
          <section :key="field.id" v-for="field in fields">
            <div
              style="margin-top: -2rem; margin-left: -0.5rem"
              v-if="field.apiName === 'meeting_type'"
            >
              <span class="input-container">
                <label class="label">Title</label>
                <input
                  id="user-input"
                  type="text"
                  style="width: 40.25vw"
                  v-model="noteTitle"
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                />
              </span>
            </div>
            <div
              style="margin-top: -4rem; margin-left: -0.5rem; position: relative"
              v-else-if="field.apiName === 'meeting_comments'"
            >
              <span class="input-container">
                <label class="label">Note</label>
                <div
                  @input="setUpdateValues(field.apiName, $event.target.innerHTML)"
                  class="divArea"
                  v-html="noteValue"
                  contenteditable="true"
                ></div>
              </span>
              <section v-if="!addingTemplate" class="note-templates">
                <span
                  v-if="noteTemplates.length"
                  @click="addingTemplate = !addingTemplate"
                  class="note-templates__content"
                >
                  Insert Template <img src="@/assets/images/note.svg" alt="" />
                </span>
                <span @click="goToProfile" class="note-templates__content" v-else>
                  Create a template <img src="@/assets/images/note.svg" alt=""
                /></span>
              </section>

              <section class="note-templates2" v-else>
                <div
                  v-for="(template, i) in noteTemplates"
                  :key="i"
                  @click="setTemplate(template.body, field.apiName, template.subject)"
                  class="note-templates2__content"
                >
                  {{ template.subject }}
                </div>
              </section>

              <div
                v-if="addingTemplate"
                @click="addingTemplate = !addingTemplate"
                class="close-template"
              >
                <img src="@/assets/images/close.svg" height="20px" alt="" />
              </div>
            </div>
            <div
              v-else-if="
                field.dataType === 'TextArea' || (field.length > 250 && field.dataType === 'String')
              "
            >
              <label class="label">{{ field.referenceDisplayLabel }}:</label>
              <textarea
                id="user-input"
                ccols="30"
                rows="4"
                :placeholder="currentVals[field.apiName]"
                style="width: 40.25vw; border-radius: 0.4rem; padding: 7px"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div
              v-else-if="
                field.dataType === 'Email' ||
                (field.dataType === 'String' && field.apiName !== 'meeting_type') ||
                (field.dataType === 'String' && field.apiName !== 'meeting_comments') ||
                (field.dataType === 'String' && field.apiName !== 'NextStep')
              "
              class="col"
            >
              <label class="label">{{ field.referenceDisplayLabel }}:</label>
              <input
                id="user-input"
                type="text"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.apiName === 'AccountId'">
              <label class="label">{{ field.referenceDisplayLabel }}</label>
              <Multiselect
                v-model="selectedAccount"
                :options="allAccounts"
                @search-change="getAccounts($event)"
                @select="
                  setUpdateValues(
                    field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? $event.value
                      : $event.id,
                    field.dataType === 'MultiPicklist' ? true : false,
                  )
                "
                openDirection="below"
                style="width: 40.25vw"
                selectLabel="Enter"
                track-by="integration_id"
                label="name"
                :loading="dropdownLoading || loadingAccounts"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>

                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{ currentAccount }}
                  </p>
                </template>
              </Multiselect>
            </div>
            <div
              v-else-if="
                field.dataType === 'Picklist' ||
                field.dataType === 'MultiPicklist' ||
                (field.dataType === 'Reference' && field.apiName !== 'AccountId') ||
                (field.dataType === 'Reference' && field.apiName !== 'OwnerId')
              "
            >
              <label class="label">{{ field.referenceDisplayLabel }}:</label>
              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="
                  field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                    ? allPicklistOptions[field.apiName]
                    : referenceOpts[field.apiName]
                "
                @select="
                  setUpdateValues(
                    field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? $event.value
                      : $event.id,
                    field.dataType === 'MultiPicklist' ? true : false,
                  )
                "
                @search-change="
                  field.dataType === 'Reference'
                    ? getReferenceFieldList(field.apiName, field.id, $event)
                    : null
                "
                :multiple="field.dataType === 'MultiPicklist' ? true : false"
                openDirection="below"
                :loading="dropdownLoading"
                style="width: 40.25vw"
                selectLabel="Enter"
                :track-by="
                  field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                    ? 'value'
                    : 'id'
                "
                :label="
                  field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                    ? 'label'
                    : 'name'
                "
              >
                <template slot="noResult">
                  <p class="multi-slot">No results ? Try loading more</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{
                      `${currentVals[field.apiName]}` !== 'null'
                        ? `${currentVals[field.apiName]}`
                        : `${field.referenceDisplayLabel}`
                    }}
                  </p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more">
                    Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                  </p>
                </template>
              </Multiselect>

              <div
                :class="stageGateField ? 'adding-stage-gate' : 'hide'"
                v-if="field.apiName === 'StageName'"
              >
                <div class="adding-stage-gate__body">
                  <div v-for="(field, i) in stageValidationFields[stageGateField]" :key="i">
                    <div v-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
                      <label class="red-label">{{ field.referenceDisplayLabel }}*</label>
                      <Multiselect
                        :options="allPicklistOptions[field.apiName]"
                        @select="
                          setUpdateValidationValues(
                            field.apiName === 'ForecastCategory'
                              ? 'ForecastCategoryName'
                              : field.apiName,
                            $event.value,
                          )
                        "
                        v-model="dropdownVal[field.apiName]"
                        openDirection="below"
                        :loading="dropdownLoading"
                        style="width: 40vw; margin-bottom: 2rem"
                        selectLabel="Enter"
                        track-by="value"
                        label="label"
                        :multiple="field.dataType === 'MultiPicklist' ? true : false"
                      >
                        <template slot="noResult">
                          <p class="multi-slot">No results. Try loading more</p>
                        </template>
                        <template slot="afterList">
                          <p class="multi-slot__more">
                            Load more
                            <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                          </p>
                        </template>
                        <template slot="placeholder">
                          <p class="slot-icon">
                            <img src="@/assets/images/search.svg" alt="" />
                            {{
                              `${currentVals[field.apiName]}` !== 'null'
                                ? `${currentVals[field.apiName]}`
                                : `${field.referenceDisplayLabel}`
                            }}
                          </p>
                        </template>
                      </Multiselect>
                    </div>
                    <div v-else-if="field.dataType === 'String' && field.apiName !== 'NextStep'">
                      <label class="red-label">{{ field.referenceDisplayLabel }}*</label>
                      <input
                        id="user-input"
                        type="text"
                        :placeholder="currentVals[field.apiName]"
                        v-model="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>

                    <div
                      v-else-if="
                        field.dataType === 'TextArea' ||
                        (field.length > 250 && field.dataType === 'String')
                      "
                    >
                      <label class="red-label">{{ field.referenceDisplayLabel }}*</label>
                      <textarea
                        id="user-input"
                        ccols="30"
                        rows="2"
                        :placeholder="currentVals[field.apiName]"
                        style="width: 40.25vw; border-radius: 0.2rem; padding: 7px"
                        v-model="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      >
                      </textarea>
                    </div>
                    <div v-else-if="field.dataType === 'Date'">
                      <label class="red-label">{{ field.referenceDisplayLabel }}*</label>
                      <input
                        type="text"
                        onfocus="(this.type='date')"
                        onblur="(this.type='text')"
                        :placeholder="currentVals[field.apiName]"
                        style="width: 40.25vw"
                        v-model="currentVals[field.apiName]"
                        id="user-input"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>
                    <div v-else-if="field.dataType === 'DateTime'">
                      <label class="red-label">{{ field.referenceDisplayLabel }}*</label>
                      <input
                        type="datetime-local"
                        id="start"
                        style="width: 40.25vw"
                        v-model="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>
                    <div
                      v-else-if="
                        field.dataType === 'Phone' ||
                        field.dataType === 'Double' ||
                        field.dataType === 'Currency'
                      "
                    >
                      <label class="red-label">{{ field.referenceDisplayLabel }}*</label>
                      <input
                        id="user-input"
                        style="width: 40.25vw"
                        type="number"
                        v-model="currentVals[field.apiName]"
                        :placeholder="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>

                    <div v-else-if="field.apiName === 'OwnerId'">
                      <label class="red-label">{{ field.referenceDisplayLabel }}*</label>

                      <Multiselect
                        v-model="selectedOwner"
                        :options="allUsers"
                        @select="
                          setUpdateValidationValues(
                            field.apiName,
                            $event.salesforce_account_ref.salesforce_id,
                          )
                        "
                        openDirection="below"
                        style="width: 40.25vw"
                        selectLabel="Enter"
                        track-by="salesforce_account_ref.salesforce_id"
                        label="full_name"
                        :loading="dropdownLoading"
                      >
                        <template slot="noResult">
                          <p class="multi-slot">No results.</p>
                        </template>
                        <template slot="placeholder">
                          <p class="slot-icon">
                            <img src="@/assets/images/search.svg" alt="" />
                            {{ currentOwner }}
                          </p>
                        </template>
                      </Multiselect>
                    </div>

                    <div v-else-if="field.apiName === 'AccountId'">
                      <label class="red-label">{{ field.referenceDisplayLabel }}*</label>
                      <Multiselect
                        v-model="selectedAccount"
                        :options="allAccounts"
                        @search-change="getAccounts($event)"
                        @select="setUpdateValidationValues(field.apiName, $event.id)"
                        openDirection="below"
                        style="width: 40.25vw"
                        selectLabel="Enter"
                        track-by="integration_id"
                        label="name"
                        :loading="dropdownLoading || loadingAccounts"
                      >
                        <template slot="noResult">
                          <p class="multi-slot">No results.</p>
                        </template>

                        <template slot="placeholder">
                          <p class="slot-icon">
                            <img src="@/assets/images/search.svg" alt="" />
                            {{ currentAccount }}
                          </p>
                        </template>
                      </Multiselect>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col" v-else-if="field.dataType === 'Date'">
              <label class="label">{{ field.referenceDisplayLabel }}:</label>
              <input
                type="date"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                id="user-input"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div class="col" v-else-if="field.dataType === 'DateTime'">
              <label class="label">{{ field.referenceDisplayLabel }}:</label>
              <input
                type="datetime-local"
                id="start"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              class="col"
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency'
              "
            >
              <label class="label">{{ field.referenceDisplayLabel }}:</label>
              <input
                id="user-input"
                type="number"
                v-model="currentVals[field.apiName]"
                :placeholder="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>

            <div v-else-if="field.dataType === 'Boolean'">
              <label class="label">{{ field.referenceDisplayLabel }}:</label>

              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="booleans"
                @select="setUpdateValues(field.apiName, $event)"
                openDirection="below"
                style="width: 40.25vw"
                selectLabel="Enter"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{ currentVals[field.apiName] }}
                  </p>
                </template>
              </Multiselect>
            </div>
          </section>
          <div ref="product" class="adding-product" v-if="addingProduct">
            <div class="adding-product__header">
              <img class="fullInvert" src="@/assets/images/tag.svg" alt="" />
              <p>Add Product</p>
            </div>
            <div class="adding-product__body">
              <div v-if="!pricebookId">
                <p class="form-label">Pricebook:</p>
                <Multiselect
                  @select="getPricebookEntries($event.integration_id)"
                  :options="pricebooks"
                  v-model="selectedPriceBook"
                  openDirection="below"
                  style="width: 36vw"
                  selectLabel="Enter"
                  label="name"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      {{ 'Pricebook' }}
                    </p>
                  </template>
                </Multiselect>
              </div>
              <div v-for="(field, i) in createProductForm" :key="i">
                <div
                  v-if="
                    field.dataType === 'Picklist' ||
                    field.dataType === 'MultiPicklist' ||
                    field.dataType === 'Reference'
                  "
                >
                  <p class="form-label">
                    {{
                      field.referenceDisplayLabel === 'PricebookEntry'
                        ? 'Products'
                        : field.referenceDisplayLabel
                    }}:
                  </p>
                  <Multiselect
                    :options="
                      field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                        ? allPicklistOptions[field.id]
                        : productReferenceOpts[field.apiName]
                    "
                    @select="
                      setCreateValues(
                        field.apiName === 'ForecastCategory'
                          ? 'ForecastCategoryName'
                          : field.apiName,
                        field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                          ? $event.value
                          : field.apiName === 'PricebookEntryId'
                          ? $event.integration_id
                          : $event.id,
                      )
                    "
                    :loading="loadingProducts"
                    openDirection="below"
                    v-model="dropdownVal[field.apiName]"
                    style="width: 36vw"
                    selectLabel="Enter"
                    :track-by="
                      field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                        ? 'value'
                        : 'id'
                    "
                    :label="
                      field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                        ? 'label'
                        : 'name'
                    "
                  >
                    <template slot="afterList">
                      <p v-if="showLoadMore" @click="loadMore" class="multi-slot__more">
                        Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                      </p>
                    </template>
                    <template slot="noResult">
                      <p class="multi-slot">No results.</p>
                    </template>
                    <template slot="placeholder">
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        {{ field.referenceDisplayLabel }}
                      </p>
                    </template>
                  </Multiselect>
                </div>

                <div v-else-if="field.dataType === 'String'">
                  <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
                  <input
                    id="user-input"
                    type="text"
                    style="width: 36vw"
                    :disabled="savingCreateForm"
                    :placeholder="currentVals[field.apiName]"
                    v-model="currentVals[field.apiName]"
                    @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                  />
                </div>

                <div
                  v-else-if="
                    field.dataType === 'TextArea' ||
                    (field.length > 250 && field.dataType === 'String')
                  "
                >
                  <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
                  <textarea
                    id="user-input"
                    ccols="30"
                    rows="2"
                    :disabled="savingCreateForm"
                    :placeholder="currentVals[field.apiName]"
                    style="width: 36vw; border-radius: 6px; padding: 7px"
                    v-model="currentVals[field.apiName]"
                    @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                  >
                  </textarea>
                </div>
                <div v-else-if="field.dataType === 'Date'">
                  <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
                  <input
                    type="text"
                    onfocus="(this.type='date')"
                    onblur="(this.type='text')"
                    style="width: 36vw"
                    :disabled="savingCreateForm"
                    :placeholder="currentVals[field.apiName]"
                    v-model="currentVals[field.apiName]"
                    id="user-input"
                    @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                  />
                </div>
                <div v-else-if="field.dataType === 'DateTime'">
                  <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
                  <input
                    type="datetime-local"
                    id="start"
                    style="width: 36vw"
                    :disabled="savingCreateForm"
                    v-model="currentVals[field.apiName]"
                    @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                  />
                </div>
                <div
                  v-else-if="
                    field.dataType === 'Phone' ||
                    field.dataType === 'Double' ||
                    field.dataType === 'Currency'
                  "
                >
                  <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
                  <input
                    id="user-input"
                    type="number"
                    style="width: 36vw"
                    :disabled="savingCreateForm"
                    v-model="currentVals[field.apiName]"
                    :placeholder="currentVals[field.apiName]"
                    @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                  />
                </div>
              </div>
            </div>
          </div>
          <!-- <button>Add product</button> -->
        </div>
        <div class="flex-end-opp">
          <div v-if="hasProducts && resource === 'Opportunity'">
            <button
              v-if="!addingProduct"
              @click="addProduct"
              style="margin-bottom: 0.75rem"
              class="select-btn1"
            >
              Add Product
            </button>

            <p @click="addProduct" v-else class="product-text">
              Adding product <img src="@/assets/images/remove.svg" alt="" />
            </p>
          </div>
          <div v-else></div>
          <div style="display: flex; align-items: center">
            <button
              @click="
                onMakeMeetingUpdate()
                createProduct()
              "
              class="add-button__"
            >
              Update
            </button>
            <p @click="resetEdit" class="cancel">Cancel</p>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>
<script>
import Modal from '@/components/InviteModal'

export default {
  name: 'UpdateForm',
  components: {
    Modal,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      addingTemplate: false,
      accountSelected: this.selectedAccount,
      selectedPricebookCopy: this.selectedPricebook,
      booleans: ['true', 'false'],
      selectedPriceBook: null,
    }
  },
  methods: {
    loadMore() {
      this.$emit('load-more')
    },
    getAccounts(i) {
      this.$emit('get-accounts', i)
    },
    resetEdit() {
      this.$emit('reset-edit')
    },
    addProduct() {
      this.$emit('add-product')
      setTimeout(() => {
        this.$refs.product ? this.$refs.product.scrollIntoView() : null
      }, 100)
    },
    setUpdateValues(arg, arg2) {
      this.$emit('set-update-values', arg, arg2)
    },
    setCreateValues(arg, arg2) {
      this.$emit('set-create-values', arg, arg2)
    },
    setUpdateValidationValues(arg, arg2) {
      this.$emit('set-validation-values', arg, arg2)
    },
    setTemplate(arg1, arg2, arg3) {
      this.$emit('set-template', arg1, arg2, arg3)
    },
    updateResource() {
      this.$emit('update-resource')
    },
    onMakeMeetingUpdate() {
      this.$emit('update-meeting')
    },
    createProduct() {
      this.$emit('create-product')
    },
    getPricebookEntries(arg) {
      this.$emit('get-pricebooks', arg)
    },
  },
  props: {
    resource: {
      default: 'Opportunity',
    },
    fields: {},
    currentVals: {},
    dropdownVal: {},
    noteTitle: {},
    noteValue: {},
    allAccounts: {},
    selectedAccount: {},
    hasProducts: {},
    allPicklistOptions: {},
    productReferenceOpts: {},
    pricebooks: {},
    noteTemplates: {},
    dropdownLoading: {},
    stageGateField: {},
    stageValidationFields: {},
    currentAccount: {},
    referenceOpts: {},
    loadingAccounts: {},
    currentOwner: {},
    addingProduct: {},
    pricebookId: {},
    createProductForm: {},
    loadingProducts: {},
    savingCreateForm: {},
    showLoadMore: {},
    stagePicklistQueryOpts: {},
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';

@mixin epic-sides() {
  position: relative;
  z-index: 1;

  &:before {
    position: absolute;
    content: '';
    display: block;
    top: 0;
    left: -5000px;
    height: 100%;
    width: 15000px;
    z-index: -1;
    @content;
  }
}
.red-label {
  background-color: #fa646a;
  color: white;
  display: inline-block;
  padding: 6px;
  font-size: 14px;
  text-align: center;
  min-width: 80px;
  margin-top: 12px;
  margin-left: 2px;
  font-weight: bold;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
.opp-modal-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: white;
  width: 44vw;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #e8e8e8;
}
#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2.5rem;
  width: 40.25vw;
  font-family: $base-font-family;
}
#user-input:focus {
  outline: none;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.header {
  font-size: 18px;
  padding: 0;
  letter-spacing: 0.5px;
  margin-bottom: 0.2rem;
}

.input-container {
  position: relative;
  display: inline-block;
  margin: 30px 10px;
  @include epic-sides() {
    background: inherit;
  }
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  letter-spacing: 1px;
  h4 {
    font-size: 20px;
  }
}
.opp-modal {
  width: 42vw;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: 56vh;
  color: $base-gray;
  font-size: 16px;
  letter-spacing: 0.75px;
  div {
    margin-right: -1.25rem;
  }
}
.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.label {
  display: inline-block;
  padding: 6px;
  font-size: 14px;
  text-align: center;
  min-width: 80px;
  margin-top: 12px;
  background-color: $white-green;
  color: $dark-green;
  font-weight: bold;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
.close-template {
  position: absolute;
  bottom: 56px;
  right: 20px;
  z-index: 3;
  cursor: pointer;
  background-color: black;
  border-radius: 3px;
  opacity: 0.6;
  img {
    filter: invert(99%);
  }
}
.logo {
  height: 24px;
  margin-left: 0.5rem;
  margin-right: 0.25rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.divArea {
  -moz-appearance: textfield-multiline;
  -webkit-appearance: textarea;
  resize: both;
  height: 30px;
  width: 40.25vw;
  min-height: 20vh;
  margin-bottom: 4px;
  border: 1px solid #e8e8e8;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  overflow-y: scroll;
  font-family: inherit;
  font-style: inherit;
  font-size: 13px;
  padding: 12px;
}
.divArea:focus {
  outline: none;
}
.note-templates {
  display: flex;
  justify-content: flex-end;
  font-size: 12px;
  padding: 12px 6px;
  margin-top: -34px;
  margin-left: 10px;
  border: 1px solid $soft-gray;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  cursor: pointer;
  width: 40.25vw;

  &__content {
    display: flex;
    flex-direction: row;
    align-items: center;
  }
  img {
    filter: invert(50%);
    height: 12px;
  }
  &__content:hover {
    opacity: 0.6;
  }
}

.note-templates2 {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 24px;
  font-size: 12px;
  padding: 12px 6px;
  margin-top: -34px;
  margin-left: 10px;
  border: 1px solid $soft-gray;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  width: 40.25vw;
  height: 80px;
  overflow: scroll;

  &__content {
    border-radius: 4px;
    border: 0.5px solid $base-gray;
    color: $base-gray;
    padding: 8px 6px;
    margin-bottom: 8px;
    cursor: pointer;
  }
  &__content:hover {
    opacity: 0.6;
  }
}
.adding-stage-gate {
  // border: 1px solid $coral;
  border-radius: 0.3rem;
  margin: 0.5rem 0rem;
  width: 40.25vw;
  // min-height: 30vh;
  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    font-size: 14px;
    padding: 0.5rem;
    color: $white;
    width: 100%;
    // border-bottom: 1px solid $coral;
    // background-color: $coral;
    img {
      height: 1rem;
      margin-right: 0.5rem;
    }
  }
  &__body {
    padding: 0.25rem;
    font-size: 11px !important;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.2rem;
    overflow: auto;
    margin-left: -6px;
    // height: 30vh;
    input {
      width: 10vw;
      height: 1.5rem !important;
    }
    .multiselect {
      width: 12vw;
      font-weight: 11px !important;
    }
    p {
      margin-left: 0.25rem;
    }
    span {
      // color: $coral;
    }
  }

  &__body::-webkit-scrollbar {
    width: 2px; /* Mostly for vertical scrollbars */
    height: 0px; /* Mostly for horizontal scrollbars */
  }
  &__body::-webkit-scrollbar-thumb {
    background-color: $coral;
    box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track {
    box-shadow: inset 2px 2px 4px 0 $soft-gray;
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track-piece {
    margin-top: 0.25rem;
  }
}
.hide {
  display: none;
}
.flex-end-opp {
  width: 100%;
  padding: 0.25rem 1.5rem;
  height: 4rem;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}
.product-text {
  display: flex;
  align-items: center;
  color: $dark-green;
  border-radius: 4px;
  padding: 4px 6px;
  background-color: $white-green;
  font-size: 14px;
  letter-spacing: 0.5px;
  font-weight: bold;
  cursor: pointer;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
    height: 16px;
    margin-left: 4px;
  }
}
.select-btn1 {
  border: 0.7px solid $dark-green;
  padding: 0.45rem 1.25rem;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  color: $dark-green;
  letter-spacing: 0.2px;
  margin-right: 0.5rem;
  transition: all 0.25s;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
.add-button__ {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.4rem 0.75rem;
  font-size: 14px;
  border-radius: 6px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
}
.add-button__:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.cancel {
  color: $dark-green;
  font-weight: bold;
  margin-left: 1rem;
  cursor: pointer;
}
input {
  padding: 7px;
}
.adding-product {
  border: 1px solid $dark-green;
  border-radius: 0.3rem;
  margin: 0.5rem 0rem;
  width: 40.5vw;
  min-height: 30vh;
  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    font-size: 14px;
    padding: 0.5rem;
    color: $white;
    width: 100%;
    border-bottom: 1px solid $dark-green;
    background-color: $dark-green;
    img {
      height: 1rem;
      margin-right: 0.5rem;
    }
  }
  &__body {
    padding: 0.25rem;
    font-size: 11px !important;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.2rem;
    overflow: auto;
    height: 30vh;
    input {
      width: 10vw;
      height: 1.5rem !important;
    }
    .multiselect {
      width: 12vw;
      font-weight: 11px !important;
    }
    p {
      margin-left: 0.25rem;
    }
    span {
      color: $coral;
    }
  }

  &__body::-webkit-scrollbar {
    width: 2px; /* Mostly for vertical scrollbars */
    height: 0px; /* Mostly for horizontal scrollbars */
  }
  &__body::-webkit-scrollbar-thumb {
    background-color: $dark-green;
    box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track {
    box-shadow: inset 2px 2px 4px 0 $soft-gray;
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track-piece {
    margin-top: 0.25rem;
  }
}

.fullInvert {
  filter: invert(99%);
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 11px;
  width: 100%;
  padding: 0;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    // border-top: 1px solid #e8e8e8;
    width: 100%;
    height: 40px;
    padding: 4px 0px 6px 0px;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
</style>