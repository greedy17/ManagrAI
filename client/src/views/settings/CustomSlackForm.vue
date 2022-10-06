<template>
  <div class="slack-form-builder">
    <Modal
      v-if="customObjectModal"
      dimmed
    >
      <div class="opp-modal-container">
        <div v-if="modalLoading">
          <Loader :loaderText="loaderText" />
        </div>
        <div v-else>
          <div class="flex-row-spread header">
            <div class="flex-row">
              <img src="@/assets/images/logo.png" class="logo" height="26px" alt="" />
              <h3>Add Custom Object</h3>
            </div>
            <img
              src="@/assets/images/close.svg"
              style="height: 1.25rem; margin-top: -1rem; margin-right: 0.75rem; cursor: pointer"
              @click="toggleCustomObjectModal"
              alt=""
            />
          </div>
          <div class="opp-modal">
            <section>
              <div style="display: flex; justify-content: space-between;">
                <!-- <label class="modal-label">Label</label>
                <textarea
                  id="user-input"
                  cols="30"
                  rows="4"
                  :disabled="false"
                  style="width: 40.25vw; border-radius: 0.4rem"
                  @input="() => null"
                >
                </textarea> -->
                <Multiselect
                  @input="getCustomObjectFields"
                  :options="customObjects"
                  openDirection="below"
                  style="width: 20vw; margin-top: 2rem; margin-left: 1rem;"
                  selectLabel="Enter"
                  label="custom"
                  v-model="selectedCustomObject"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
  
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Custom Object
                    </p>
                  </template>
                </Multiselect>
                <div v-if="selectedCustomObject" class="field-section">
                  <div class="search-bar">
                    <img src="@/assets/images/search.svg" style="height: 18px; cursor: pointer" alt="" />
                    <input type="search" placeholder="Search Custom Object Fields" v-model="COfilterText" />
                  </div>
  
                  <div class="field-section__fields">
                    <div style="height: 45vh; overflow: scroll">
                      <p v-for="(field, i) in COfilteredFields" :key="field.id">
                        <input @click="onAddField(field)" type="checkbox" :id="i" :value="field" />
                        <label :for="i"></label>
                        {{ field.label }}
                        <span v-if="field.required" class="red-text">required</span>
                      </p>
                    </div>
                  </div>
                </div>
                <!-- <div class="flex-end-opp">
                  <div v-if="true" style="display: flex; align-items: center">
                    <button class="add-button" @click="() => null">
                      Save
                    </button>
                    <p @click="toggleCustomObjectModal" class="cancel">Cancel</p>
                  </div>
                </div> -->
              </div>
            </section>
          </div>
        </div>
      </div>
    </Modal>
    <section class="wrapper">
      <div class="tabs">
        <div class="tab">
          <input type="radio" name="css-tabs" id="tab-1" checked class="tab-switch" />
          <label for="tab-1" class="tab-label" @click="changeToOpportunity">Opportunity</label>
          <div class="tab-content">
            <section>
              <div class="tab-content__div">
                <p @click="switchFormType" class="form-type">
                  {{ camelize(newFormType) }} {{ camelize(newResource) }}
                  <img src="@/assets/images/shuffle.svg" height="12px" alt="" />
                </p>
                <div>
                  <button @click="onSave" class="save">Save Form</button>
                </div>
              </div>
              <div id="formSection">
                <draggable
                  v-model="addedFields"
                  group="fields"
                  @start="drag = true"
                  @end="drag = false"
                  class="drag-section"
                >
                  <div v-for="field in addedFields" :key="field.id">
                    <div v-if="!unshownIds.includes(field.id)">
                      <div class="drag-item">
                        <p id="formField" :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                          <img src="@/assets/images/drag.svg" alt="" />
                          {{ field.label }}
                        </p>
                        <img
                          src="@/assets/images/trash.svg"
                          alt=""
                          id="remove"
                          :class="unshownIds.includes(field.id) ? 'invisible' : 'invert'"
                          @click="
                            () => {
                              onRemoveField(field)
                            }
                          "
                        />
                      </div>
                    </div>
                  </div>
                </draggable>
              </div>
            </section>
          </div>
        </div>
        <div class="tab">
          <input type="radio" name="css-tabs" id="tab-2" class="tab-switch" />
          <label for="tab-2" class="tab-label" @click="changeToStage">Stage Related</label>
          <div class="tab-content">
            <section class="space-between">
              <h3 v-if="!selectedForm && !currentlySelectedForm" class="form-type">
                Add/edit your stage related forms
              </h3>
              <h3 v-else-if="selectedForm">
                {{ selectedForm.stage + ' Form' }}
              </h3>
              <h3 v-else>{{ currentlySelectedForm }}</h3>
              <div>
                <img
                  @click="selectedForm = null"
                  v-if="selectedForm"
                  style="margin-right: 16px"
                  src="@/assets/images/left.svg"
                  height="13px"
                  alt=""
                />
                <button v-if="selectedForm" @click="toggleCustomObjectModal" class="custom-object-button">
                  Add Custom Object
                </button>
                <button
                  v-if="selectedForm && selectedForm.fields.length"
                  @click.prevent="deleteForm(activeForm)"
                  class="delete"
                >
                  Delete Form
                </button>
                <button @click="onSave" class="save">Save Form</button>
              </div>
            </section>

            <div>
              <!-- <Multiselect
                v-if="!formLength && !addingForm"
                @input="selectForm('Opportunity', 'STAGE_GATING', $event.stage)"
                :options="formStages"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="stage"
                label="stage"
                v-model="currentlySelectedForm"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>

                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Edit Stage form
                  </p>
                </template>
              </Multiselect> -->

              <div class="row__">
                <Multiselect
                  v-if="!selectedForm"
                  @input="setStage($event)"
                  :options="stages"
                  openDirection="below"
                  style="width: 20vw"
                  selectLabel="Enter"
                  track-by="value"
                  label="label"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>

                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      {{ selectedStage ? selectedStage : 'Select stage' }}
                    </p>
                  </template>
                </Multiselect>
              </div>
            </div>

            <div v-if="selectedForm" id="formSection">
              <draggable
                v-model="addedFields"
                group="fields"
                @start="drag = true"
                @end="drag = false"
                class="drag-section"
              >
                <div v-for="field in addedFields" :key="field.id">
                  <div v-if="!unshownIds.includes(field.id)">
                    <div class="drag-item">
                      <p id="formField" :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                        <img src="@/assets/images/drag.svg" alt="" />
                        {{ field.label }}
                      </p>
                      <img
                        src="@/assets/images/trash.svg"
                        alt=""
                        id="remove"
                        :class="unshownIds.includes(field.id) ? 'invisible' : 'invert'"
                        @click="
                          () => {
                            onRemoveField(field)
                          }
                        "
                      />
                    </div>
                  </div>
                </div>
              </draggable>
            </div>
          </div>
        </div>
        <div class="tab">
          <input type="radio" name="css-tabs" id="tab-3" class="tab-switch" />
          <label for="tab-3" class="tab-label" @click="changeToAccount">Account</label>
          <div class="tab-content">
            <section>
              <div class="tab-content__div">
                <p @click="switchFormType" class="form-type">
                  {{ camelize(newFormType) }} {{ camelize(newResource) }}
                  <img src="@/assets/images/shuffle.svg" height="12px" alt="" />
                </p>
                <div>
                  <button @click="onSave" class="save">Save Form</button>
                </div>
              </div>
              <div id="formSection">
                <draggable
                  v-model="addedFields"
                  group="fields"
                  @start="drag = true"
                  @end="drag = false"
                  class="drag-section"
                >
                  <div v-for="field in addedFields" :key="field.id">
                    <div v-if="!unshownIds.includes(field.id)">
                      <div class="drag-item">
                        <p id="formField" :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                          <img src="@/assets/images/drag.svg" alt="" />
                          {{ field.label }}
                        </p>
                        <img
                          src="@/assets/images/trash.svg"
                          alt=""
                          id="remove"
                          :class="unshownIds.includes(field.id) ? 'invisible' : 'invert'"
                          @click="
                            () => {
                              onRemoveField(field)
                            }
                          "
                        />
                      </div>
                    </div>
                  </div>
                </draggable>
              </div>
            </section>
          </div>
        </div>
        <div class="tab">
          <input type="radio" name="css-tabs" id="tab-4" class="tab-switch" />
          <label for="tab-4" class="tab-label" @click="changeToContact">Contact</label>
          <div class="tab-content">
            <section>
              <div class="tab-content__div">
                <p @click="switchFormType" class="form-type">
                  {{ camelize(newFormType) }} {{ camelize(newResource) }}
                  <img src="@/assets/images/shuffle.svg" height="12px" alt="" />
                </p>
                <div>
                  <button @click="onSave" class="save">Save Form</button>
                </div>
              </div>
              <div id="formSection">
                <draggable
                  v-model="addedFields"
                  group="fields"
                  @start="drag = true"
                  @end="drag = false"
                  class="drag-section"
                >
                  <div v-for="field in addedFields" :key="field.id">
                    <div v-if="!unshownIds.includes(field.id)">
                      <div class="drag-item">
                        <p id="formField" :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                          <img src="@/assets/images/drag.svg" alt="" />
                          {{ field.label }}
                        </p>
                        <img
                          src="@/assets/images/trash.svg"
                          alt=""
                          id="remove"
                          :class="unshownIds.includes(field.id) ? 'invisible' : 'invert'"
                          @click="
                            () => {
                              onRemoveField(field)
                            }
                          "
                        />
                      </div>
                    </div>
                  </div>
                </draggable>
              </div>
            </section>
          </div>
        </div>
        <div class="tab">
          <input type="radio" name="css-tabs" id="tab-5" class="tab-switch" />
          <label for="tab-5" class="tab-label" @click="changeToLead">Lead</label>
          <div class="tab-content">
            <section>
              <div class="tab-content__div">
                <p @click="switchFormType" class="form-type">
                  {{ camelize(newFormType) }} {{ camelize(newResource) }}
                  <img src="@/assets/images/shuffle.svg" height="12px" alt="" />
                </p>
                <div>
                  <button @click="onSave" class="save">Save Form</button>
                </div>
              </div>
              <div id="formSection">
                <draggable
                  v-model="addedFields"
                  group="fields"
                  @start="drag = true"
                  @end="drag = false"
                  class="drag-section"
                >
                  <div v-for="field in addedFields" :key="field.id">
                    <div v-if="!unshownIds.includes(field.id)">
                      <div class="drag-item">
                        <p id="formField" :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                          <img src="@/assets/images/drag.svg" alt="" />
                          {{ field.label }}
                        </p>
                        <img
                          src="@/assets/images/trash.svg"
                          alt=""
                          id="remove"
                          :class="unshownIds.includes(field.id) ? 'invisible' : 'invert'"
                          @click="
                            () => {
                              onRemoveField(field)
                            }
                          "
                        />
                      </div>
                    </div>
                  </div>
                </draggable>
              </div>
            </section>
          </div>
        </div>
      </div>
    </section>
    <div class="field-section">
      <div class="search-bar">
        <img src="@/assets/images/search.svg" style="height: 18px; cursor: pointer" alt="" />
        <input type="search" placeholder="Search Opportunity Fields" v-model="filterText" />
      </div>

      <div class="field-section__fields">
        <div style="height: 85vh; overflow: scroll">
          <!-- <section>
            <p key="name"><input type="checkbox" /> Name <span>required</span></p>
            <p><input type="checkbox" /> Stage <span>required</span></p>
            <p>
              <input type="checkbox" /> Close Date
              <span>required</span>
            </p>
          </section> -->

          <p v-for="(field, i) in filteredFields" :key="field.id">
            <input @click="onAddField(field)" type="checkbox" :id="i" :value="field" />
            <label :for="i"></label>
            {{ field.label }}
            <span v-if="field.required" class="red-text">required</span>
          </p>
        </div>
      </div>
    </div>

    <!-- <div class="opportunity__row">
      <div :class="formType !== 'STAGE_GATING' ? 'collection_fields' : 'stage_fields'">
        <div class="sticky">
          <p>{{ camelize(formType)  + {{camelize(resource)}} ' ' + resource }} Form</p>
        </div>

        <div>
          <div v-if="formType === 'STAGE_GATING'">
            <div class="center">
              <button
                v-if="!addingFields"
                @click="
                  () => {
                    addingFields = !addingFields
                  }
                "
                class="default_button"
              >
                Add Fields
                <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
              </button>
            </div>
          </div>
        </div>

        <div v-if="resource === 'Contact' || resource === 'Lead' || resource === 'Account'">
          <p>{{ formType + ' ' + resource }} Form</p>
          <div v-if="formType === 'CREATE'">
            <div
              v-if="
                (!addedFieldNames.includes('LastName') &&
                  (resource === 'Contact' || resource === 'Lead')) ||
                (!addedFieldNames.includes('LastName') && resource === 'Account')
              "
              class="centered"
            >
              <p style="margin-left: 0.5rem">
                {{ resource === 'Account' ? 'Account Name' : 'Last Name'
                }}<span style="color: #fa646a">*</span>
              </p>
              <Multiselect
                :placeholder="
                  resource === 'Account' ? `Search for Account` : `Search for 'Last Name'`
                "
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{ resource === 'Account' ? `Search for 'Account'` : `Search for 'Last Name'` }}
                  </p>
                </template>
              </Multiselect>
            </div>
            <div
              v-if="!addedFieldNames.includes('Company') && resource === 'Lead'"
              class="centered"
            >
              <p style="margin-left: 0.5rem">Company<span style="color: #fa646a">*</span></p>
              <Multiselect
                placeholder="Search for 'Company'"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Search for 'Company'
                  </p>
                </template>
              </Multiselect>
            </div>
            <div v-if="!addedFieldNames.includes('Status') && resource === 'Lead'" class="centered">
              <p style="margin-left: 0.5rem">Status<span style="color: #fa646a">*</span></p>
              <Multiselect
                placeholder="Search for 'Status'"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Search for 'Status'
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>

        <div v-if="resource === 'Opportunity' && formType !== 'STAGE_GATING'">
          <div v-if="!addedFieldLabels.includes('Name')" class="centered">
            <p style="margin-left: 0.5rem">Name: <span style="color: #fa646a">*</span></p>
            <Multiselect
              placeholder="Search for 'Name'"
              :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
              @input="onAddField($event)"
              openDirection="below"
              style="width: 20vw"
              selectLabel="Enter"
              track-by="apiName"
              label="referenceDisplayLabel"
              :loading="dropdownLoading"
            >
              <template slot="noResult">
                <p class="multi-slot">No results. Try loading more</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">
                  Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                </p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  Search for 'Name'
                </p>
              </template>
            </Multiselect>
          </div>

          <div v-if="!addedFieldNames.includes('StageName')" class="centered">
            <div class="row__">
              <p style="margin-left: 0.5rem">Stage <span style="color: #fa646a">*</span></p>
            </div>
            <Multiselect
              placeholder="Search for 'Stage'"
              :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
              @input="onAddField($event)"
              openDirection="below"
              style="width: 20vw"
              selectLabel="Enter"
              track-by="apiName"
              label="referenceDisplayLabel"
            >
              <template slot="noResult">
                <p class="multi-slot">No results. Try loading more</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">
                  Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                </p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  Search for 'Stage'
                </p>
              </template>
            </Multiselect>
          </div>

          <div v-if="!addedFieldNames.includes('CloseDate')" class="centered">
            <div class="row__">
              <p style="margin-left: 0.5rem">Close Date <span style="color: #fa646a">*</span></p>
            </div>

            <Multiselect
              placeholder="Search for 'Close Date'"
              :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
              @input="onAddField($event)"
              openDirection="below"
              style="width: 20vw"
              selectLabel="Enter"
              track-by="apiName"
              label="referenceDisplayLabel"
            >
              <template slot="noResult">
                <p class="multi-slot">No results. Try loading more</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">
                  Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                </p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  Search for 'Close Date'
                </p>
              </template>
            </Multiselect>
          </div>

          <div
            v-if="!userHasProducts && !addedFieldNames.includes('Amount') && formType !== 'CREATE'"
            class="centered"
          >
            <div class="row__">
              <div style="margin-left: 0.5rem" class="centered">
                <label :class="!productSelected ? 'green' : 'label'">Amount</label>
                <ToggleCheckBox
                  style="margin-left: 0.15rem; margin-right: 0.15rem"
                  :value="productSelected"
                  @input="productSelect"
                  offColor="#41b883"
                  onColor="#41b883"
                />
                <label style="margin-right: 0.15rem" :class="productSelected ? 'green' : 'label'"
                  >Products</label
                >
              </div>
              <p style="font-size: 12px; color: #9b9b9b; margin-left: 0.5rem">(Optional)</p>
            </div>
            <div v-if="!productSelected">
              <Multiselect
                placeholder="Search for 'Amount'"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 16vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Search for 'Amount'
                  </p>
                </template>
              </Multiselect>
            </div>

            <div v-if="productSelected">Add products on the next page</div>
          </div>
        </div>

        <p class="section-title">
          Organize your form fields:
          <span style="color: #41b883; font-size: 11px; margin-left: 0.5rem">*drag and drop</span>
        </p>

        <draggable
          style="margin-top: 0.5rem"
          v-model="addedFields"
          group="fields"
          @start="drag = true"
          @end="drag = false"
        >
          <div v-for="field in addedFields" :key="field.id">
            <div :class="unshownIds.includes(field.id) ? 'invisible' : 'centered'">
              <div class="drag-item">
                <img
                  :class="unshownIds.includes(field.id) ? 'invisible' : 'invert2'"
                  src="@/assets/images/drag.svg"
                  id="drag"
                  style="height: 1rem; width: auto; cursor: grab"
                  alt=""
                />
                <p :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                  {{ field.referenceDisplayLabel }}
                </p>
              </div>

              <div class="img-border">
                <img
                  src="@/assets/images/trash.svg"
                  alt=""
                  id="remove"
                  :class="unshownIds.includes(field.id) ? 'invisible' : 'invert'"
                  @click="
                    () => {
                      onRemoveField(field)
                    }
                  "
                />
              </div>
            </div>
          </div>
        </draggable>

        <div
          v-if="
            resource === 'Opportunity' ||
            (resource === 'Contact' &&
              !addingFields &&
              addedFieldNames.includes('LastName') &&
              formType === 'CREATE') ||
            (!addingFields && formType === 'UPDATE' && resource === 'Contact') ||
            resource === 'OpportunityLineItem' ||
            (!addingFields && formType === 'UPDATE' && resource === 'Lead') ||
            (resource === 'Lead' &&
              requiredLeadFields.every((i) => addedFieldNames.includes(i)) &&
              formType === 'CREATE') ||
            (resource === 'Account' &&
              !addingFields &&
              addedFieldNames.includes('Name') &&
              formType === 'CREATE') ||
            (!addingFields && formType === 'UPDATE' && resource === 'Account')
          "
          :style="
            resource === 'Opportunity'
              ? `
              display: flex; 
              align-items: center; 
              justify-content: center;
            `
              : `
              display: flex;
              align-items: center;
              justify-content: center;
              flex-direction: column;
              margin-top: 0.5rem;
            `
          "
        >
          <button
            v-if="
              requiredOpportunityFields.every((i) => addedFieldNames.includes(i)) ||
              resource !== 'Opportunity'
            "
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            class="default_button"
          >
            {{
              !addingFields && formType === 'UPDATE' && resource === 'Contact'
                ? `Add fields`
                : `Add more fields`
            }}
            <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
          </button>
        </div>

        <div class="example--footer">
          <PulseLoadingSpinnerButton
            v-if="
              resource === 'Opportunity' &&
              !productSelected &&
              !userHasProducts &&
              formType === 'UPDATE'
            "
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
            :disabled="!requiredOpportunityFields.every((i) => addedFieldNames.includes(i))"
          />
          <PulseLoadingSpinnerButton
            v-if="resource === 'Opportunity' && !productSelected && formType === 'CREATE'"
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
          />

          <div
            v-if="
              resource === 'Opportunity' &&
              (productSelected || userHasProducts) &&
              formType !== 'CREATE' &&
              formType !== 'STAGE_GATING'
            "
          >
            <button
              v-if="requiredOpportunityFields.every((i) => addedFieldNames.includes(i))"
              class="save"
              @click="goToProducts"
              style="margin-right: 4px"
            >
              Save + Continue to products
            </button>
            <button v-else class="disabled" style="margin-right: 4px">
              Save + Continue to products
            </button>
          </div>

          <PulseLoadingSpinnerButton
            v-else-if="resource === 'Contact' && formType === 'CREATE'"
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
            :disabled="!addedFieldNames.includes('LastName')"
          />
          <PulseLoadingSpinnerButton
            v-else-if="resource === 'Contact' && formType === 'UPDATE'"
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
          />

          <PulseLoadingSpinnerButton
            v-if="resource === 'OpportunityLineItem'"
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
          />

          <PulseLoadingSpinnerButton
            v-if="resource === 'Lead' || resource === 'Account'"
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
          />
          <div class="row__" v-if="formType === 'STAGE_GATING'">
            <PulseLoadingSpinnerButton
              @click="onSave"
              class="primary-button"
              text="Save"
              :loading="savingForm"
            />
            <button style="margin-right: 0.5rem" @click="goToValidations" class="disabled__">
              Cancel
            </button>
          </div>
        </div>
      </div>

      <div class="recommend" v-if="addingFields">
        <div class="recommend__header">
          <h4>{{ formType !== 'STAGE_GATING' ? 'Add More Fields' : 'Add Fields' }}</h4>
          <img
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            height="1rem"
            src="@/assets/images/close.svg"
            alt=""
          />
        </div>
        <div class="recommend__body">
          <Multiselect
            :placeholder="
              formType === 'STAGE_GATING' ? 'Search for Validation Fields' : 'Search Fields'
            "
            :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
            @input="onAddField($event)"
            openDirection="below"
            :style="
              formType === 'STAGE_GATING'
                ? 'width: 20vw; margin-top: 1.5rem'
                : 'width: 20vw; margin-top: 1rem'
            "
            selectLabel="Enter"
            :customLabel="
              ({ referenceDisplayLabel }) =>
                referenceDisplayLabel === 'PricebookEntry' ? 'Products' : referenceDisplayLabel
            "
            track-by="apiName"
            label="referenceDisplayLabel"
          >
            <template slot="noResult">
              <p class="multi-slot">No results. Try loading more</p>
            </template>
            <template slot="afterList">
              <p class="multi-slot__more" @click="onFieldsNextPage">
                Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
              </p>
            </template>
            <template slot="placeholder">
              <p class="slot-icon">
                <img src="@/assets/images/search.svg" alt="" />
                {{ formType === 'STAGE_GATING' ? 'Search for Validation Fields' : 'Search Fields' }}
              </p>
            </template>
          </Multiselect>
        </div>
      </div>
    </div> -->
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

import { CollectionManager, Pagination } from '@thinknimble/tn-models'

import Modal from '@/components/InviteModal'

import ActionChoice from '@/services/action-choices'
import draggable from 'vuedraggable'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import { mapState } from 'vuex'

import SlackOAuth from '@/services/slack'
import { SObjectField, SObjectPicklist } from '@/services/salesforce'

import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'CustomSlackForm',
  components: {
    PulseLoadingSpinnerButton,
    Modal,
    draggable,
    ToggleCheckBox,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
  },
  props: {
    stageForms: {
      type: Array,
      default: () => [],
    },
    customForm: {
      type: Object,
    },
    formType: {
      type: String,
      required: true,
      default: 'UPDATE',
    },
    resource: {
      type: String,
      required: true,
      default: 'Opportunity',
    },
    fields: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
    managrFields: {
      type: Array,
      default: () => [],
    },
    fromAdmin: {
      type: Boolean,
      default: false,
    },
    goBackAdmin: {
      type: Function,
      default: () => null,
    },
  },
  data() {
    return {
      activeForm: null,
      addingForm: false,
      currentlySelectedForm: null,
      customObjects: [{custom: 'Custom Object'}],
      selectedCustomObject: null,
      selectedForm: null,
      selectedStage: null,
      allForms: null,
      filterText: '',
      COfilterText: '',
      dropdownLoading: false,
      modalLoading: false,
      loaderText: 'Loading...',
      currentStageForm: null,
      formFields: CollectionManager.create({
        ModelClass: SObjectField,
        pagination: { size: 200 },
        filters: {
          salesforceObject: this.resource,
        },
      }),
      formFieldList: [],
      newFormType: this.formType,
      newResource: this.resource,
      newCustomForm: this.customForm,
      customSlackFormConfig: [],
      formHasChanges: false,
      savingForm: false,
      addedFields: [],
      formChanges: false,
      typeChanges: false,
      resourceChanges: false,
      removedFields: [],
      ...FORM_CONSTS,
      Pagination,
      meetingType: '',
      actionChoices: [],
      loadingMeetingTypes: false,
      requiredFields: [],
      formsByType: [],
      // requiredProductFields: ['PricebookEntryId', 'Quantity'],
      requiredOpportunityFields: ['Name', 'StageName', 'CloseDate'],
      requiredLeadFields: ['LastName', 'Company', 'Status'],
      nameValue: '',
      amountValue: '',
      closeValue: '',
      priceValue: '',
      quantityValue: '',
      lineValue: '',
      lastNameValue: '',
      leadLastNameValue: '',
      companyValue: '',
      accountNameValue: '',
      statusValue: '',
      stageValue: '',
      addingFieldValue: '',
      addingFields: false,
      productSelected: false,
      addingProducts: false,
      customObjectModal: false,
      formStages: [],
      stages: [],
      noteTitle: {
        _fields: {
          length: {
            defaultVal: null,
            readOnly: false,
          },
          id: {
            defaultVal: '',
            readOnly: true,
          },
          apiName: {
            defaultVal: '',
            readOnly: false,
          },
          custom: {
            defaultVal: false,
            readOnly: false,
          },
          createable: {
            defaultVal: false,
            readOnly: false,
          },
          dataType: {
            defaultVal: '',
            readOnly: false,
          },
          label: {
            defaultVal: '',
            readOnly: false,
          },
          reference: {
            defaultVal: '',
            readOnly: false,
          },
          referenceToInfos: {
            defaultVal: null,
            readOnly: false,
          },
          updateable: {
            defaultVal: false,
            readOnly: false,
          },
          required: {
            defaultVal: false,
            readOnly: false,
          },
          unique: {
            defaultVal: false,
            readOnly: false,
          },
          value: {
            defaultVal: '',
            readOnly: false,
          },
          displayValue: {
            defaultVal: '',
            readOnly: false,
          },
          referenceDisplayLabel: {
            defaultVal: '',
            readOnly: true,
          },
          filterable: {
            defaultVal: '',
            readOnly: true,
          },
          order: {
            defaultVal: null,
            readOnly: false,
          },
          includeInRecap: {
            defaultVal: null,
            readOnly: false,
          },
        },
        length: 30,
        id: '6407b7a1-a877-44e2-979d-1effafec5035',
        apiName: 'meeting_type',
        custom: true,
        createable: true,
        dataType: 'String',
        label: 'Note Subject',
        reference: 'false',
        referenceToInfos: [],
        updateable: true,
        required: false,
        unique: false,
        value: '',
        displayValue: '',
        referenceDisplayLabel: 'Note Subject',
        filterable: 'false',
        order: null,
        includeInRecap: null,
      },
      noteSubject: {
        _fields: {
          length: {
            defaultVal: null,
            readOnly: false,
          },
          id: {
            defaultVal: '',
            readOnly: true,
          },
          apiName: {
            defaultVal: '',
            readOnly: false,
          },
          custom: {
            defaultVal: false,
            readOnly: false,
          },
          createable: {
            defaultVal: false,
            readOnly: false,
          },
          dataType: {
            defaultVal: '',
            readOnly: false,
          },
          label: {
            defaultVal: '',
            readOnly: false,
          },
          reference: {
            defaultVal: '',
            readOnly: false,
          },
          referenceToInfos: {
            defaultVal: null,
            readOnly: false,
          },
          updateable: {
            defaultVal: false,
            readOnly: false,
          },
          required: {
            defaultVal: false,
            readOnly: false,
          },
          unique: {
            defaultVal: false,
            readOnly: false,
          },
          value: {
            defaultVal: '',
            readOnly: false,
          },
          displayValue: {
            defaultVal: '',
            readOnly: false,
          },
          referenceDisplayLabel: {
            defaultVal: '',
            readOnly: true,
          },
          filterable: {
            defaultVal: '',
            readOnly: true,
          },
          order: {
            defaultVal: null,
            readOnly: false,
          },
          includeInRecap: {
            defaultVal: null,
            readOnly: false,
          },
        },
        length: 255,
        id: '0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        apiName: 'meeting_comments',
        custom: true,
        createable: true,
        dataType: 'String',
        label: 'Notes',
        reference: 'false',
        referenceToInfos: [],
        updateable: true,
        required: false,
        unique: false,
        value: '',
        displayValue: '',
        referenceDisplayLabel: 'Notes',
        filterable: 'false',
        order: null,
        includeInRecap: null,
      },
    }
  },
  watch: {
    selectedStage: 'setNewForm',
    selectedForm: 'setCustomForm',
    customForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val && val.fields.length) {
          this.addedFields = [...val.fieldsRef]
          if (this.formType == 'UPDATE') {
            let currentFormFields = this.addedFields.map((field) => {
              return field.id
            })
            if (currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false) {
              let fieldsToAdd = [this.noteTitle, this.noteSubject]
              let copyArray = this.addedFields
              fieldsToAdd = fieldsToAdd.concat(copyArray)
              this.addedFields = fieldsToAdd.map((field, i) => {
                let altField = { ...field }
                altField.order = i
                if (
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5035' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
                ) {
                  altField.includeInRecap = true
                }
                return altField
              })
            }
          }
          if (this.formType !== 'UPDATE') {
            this.addedFields = this.addedFields.filter((field) => {
              return (
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
              )
            })
          }
        } else if (val && val.formType == 'STAGE_GATING' && !val.fields.length) {
          this.addedFields = []
        }
      },
    },

    newCustomForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val && val.fields.length) {
          this.addedFields = [...val.fieldsRef]
          if (this.newFormType == 'UPDATE') {
            let currentFormFields = this.addedFields.map((field) => {
              return field.id
            })
            if (currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false) {
              let fieldsToAdd = [this.noteTitle, this.noteSubject]
              let copyArray = this.addedFields
              fieldsToAdd = fieldsToAdd.concat(copyArray)
              this.addedFields = fieldsToAdd.map((field, i) => {
                let altField = { ...field }
                altField.order = i
                if (
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5035' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
                ) {
                  altField.includeInRecap = true
                }
                return altField
              })
            }
          }
          if (this.newNormType !== 'UPDATE') {
            this.addedFields = this.addedFields.filter((field) => {
              return (
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
              )
            })
          }
        } else if (val && !val.fields.length) {
          this.addedFields = []
        }
      },
    },

    resource: {
      async handler(val) {
        if (val) {
          let searchParams = this.formType
          if (searchParams.length) {
            let fieldParam = {}
            if (searchParams == this.CREATE) {
              fieldParam['createable'] = true
            } else {
              fieldParam['updateable'] = true
            }
            try {
              this.formFields.filters = {
                salesforceObject: val,

                ...fieldParam,
              }
              this.formFields.refresh()
              if (this.formType == 'UPDATE') {
                // this.onSave()
              }
            } catch (e) {
              console.log(e)
            }
          }
        }
      },
    },

    newResource: {
      async handler(val) {
        if (val) {
          let searchParams = this.formType
          if (searchParams.length) {
            let fieldParam = {}
            if (searchParams == this.CREATE) {
              fieldParam['createable'] = true
            } else {
              fieldParam['updateable'] = true
            }
            try {
              this.formFields.filters = {
                salesforceObject: val,

                ...fieldParam,
              }
              this.formFields.refresh()
              if (this.formType == 'UPDATE') {
                // this.onSave()
              }
            } catch (e) {
              console.log(e)
            }
          }
        }
      },
    },

    formType: {
      immediate: true,

      async handler(val) {
        if (val) {
          let searchParams = val
          if (searchParams.length) {
            let fieldParam = {}
            if (searchParams == this.CREATE) {
              fieldParam['createable'] = true
            } else {
              fieldParam['updateable'] = true
            }
            try {
              this.formFields.filters = {
                salesforceObject: this.resource,

                ...fieldParam,
              }
              this.formFields.refresh()
            } catch (e) {
              console.log(e)
            }
          }
        }
      },
    },

    newFormType: {
      immediate: true,

      async handler(val) {
        if (val) {
          let searchParams = val
          if (searchParams.length) {
            let fieldParam = {}
            if (searchParams == this.CREATE) {
              fieldParam['createable'] = true
            } else {
              fieldParam['updateable'] = true
            }
            try {
              this.formFields.filters = {
                salesforceObject: this.newResource,

                ...fieldParam,
              }
              this.formFields.refresh()
            } catch (e) {
              console.log(e)
            }
          }
        }
      },
    },
  },
  computed: {
    ...mapState(['user']),
    currentStagesWithForms() {
      return this.formStages.map((sf) => sf.stage)
    },
    formLength() {
      return this.formStages.length
    },
    filteredFields() {
      return this.formFields.list
        .filter((field) =>
          field.referenceDisplayLabel.toLowerCase().includes(this.filterText.toLowerCase()),
        )
        .filter((field) => !this.addedFieldNames.includes(field.apiName))
    },
    COfilteredFields() {
      return this.formFields.list
        .filter((field) =>
          field.referenceDisplayLabel.toLowerCase().includes(this.COfilterText.toLowerCase()),
        )
        .filter((field) => !this.addedFieldNames.includes(field.apiName))
    },
    currentFields() {
      return this.customForm ? this.customForm.fields : []
    },
    addedFieldIds() {
      return this.addedFields.map((field) => {
        return field.id
      })
    },
    addedFieldNames() {
      return this.addedFields.map((field) => {
        return field.apiName
      })
    },
    addedFieldLabels() {
      return this.addedFields.map((field) => {
        return field.referenceDisplayLabel
      })
    },
    unshownIds() {
      return [
        '6407b7a1-a877-44e2-979d-1effafec5035',
        '0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        'e286d1d5-5447-47e6-ad55-5f54fdd2b00d',
        'fae88a10-53cc-470e-86ec-32376c041893',
      ]
    },
    user() {
      return this.$store.state.user
    },
    userHasProducts() {
      return this.$store.state.user.organizationRef.hasProducts
    },
  },
  async created() {
    try {
      this.getActionChoices()
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
      await this.listPicklists({
        salesforceObject: this.Opportunity,
        picklistFor: 'StageName',
      })
    } catch (e) {
      console.log(e)
    }

    this.getStageForms()
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    toggleCustomObjectModal() {
      this.customObjectModal = !this.customObjectModal
    },
    getCustomObjectFields() {
      this.modalLoading = true
      setTimeout(() => {
        this.loaderText = 'Really loading...'
        setTimeout(() => {
          this.modalLoading = false;
        }, 2000)
      }, 2000)
    },
    async deleteForm(form) {
      if (form.id && form.id.length) {
        const id = form.id

        SlackOAuth.api
          .delete(id)
          .then(async (res) => {
            this.$router.go()
            this.$toast('Form removed', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
          .catch((e) => {
            this.$toast('Error, please try again', {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
          .finally(() => {})
      } else {
        const forms = this.allForms.filter((f) => {
          return f.id !== form.id
        })
        this.allForms = [...forms]
      }
    },
    setNewForm() {
      this.addForm(this.selectedStage)
      this.addingForm = false
    },
    async selectForm(resource, formType, stage = '') {
      this.selectedForm = this.allForms.find(
        (f) => f.resource == resource && f.formType == formType && f.stage == stage,
      )
      this.newFormType = formType
      this.selectedStage = stage
    },
    setCustomForm() {
      this.newCustomForm = this.selectedForm
    },
    setStage(n) {
      this.selectedStage = n.value
    },
    updateForm(event) {
      this.selectedForm = event
      let index = this.allForms.findIndex((f) => f.id == this.selectedForm.id)

      if (~index) {
        this.allForms[index] = this.selectedForm
        this.allForms = [...this.allForms]
      }
    },
    addForm(stage) {
      /** Method for Creating a new stage-gating form, this is only available for Opportunities at this time */

      if (this.currentStagesWithForms.includes(stage)) {
        this.activeForm = this.formStages.find((form) => form.stage == stage)
        // this.$toast('This stage has a form', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'default',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
      }
      let newForm = SlackOAuth.customSlackForm.create({
        resource: this.OPPORTUNITY,
        formType: this.STAGE_GATING,
        stage: stage,
      })
      newForm.fieldsRef = this.formStages.reduce((acc, curr) => {
        let fields = curr.fieldsRef.filter((f) => !acc.map((af) => af.id).includes(f.id))
        acc = [...acc, ...fields]
        return acc
      }, [])
      this.allForms = [...this.allForms, newForm]
      this.selectForm('Opportunity', 'STAGE_GATING', stage)
      this.getStageForms()
    },
    async listPicklists(query_params = {}) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)

        this.stages = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async onAddForm() {
      this.selectingStage = !this.selectingStage
      this.loadingStages = true
      try {
        await this.listPicklists({ salesforceObject: this.Opportunity, picklistFor: 'StageName' })
      } catch (e) {
        this.$modal.close('add-stage-modal')
        this.$toast('Failed to retreive stages', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loadingStages = false
      }
    },
    getStageForms() {
      // users can only create one form for the stage orderd by stage
      let forms = []
      this.stages.forEach((s) => {
        this.allForms
          .filter((f) => f.formType == this.STAGE_GATING)
          .forEach((sf) => {
            if (sf.stage == s.value) {
              forms.push(sf)
            }
          })
      })

      this.formStages = [...forms]
    },
    changeToAccount() {
      this.newResource = 'Account'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.ACCOUNT && f.formType == this.UPDATE,
      )
    },
    changeToOpportunity() {
      this.newResource = 'Opportunity'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.OPPORTUNITY && f.formType == this.UPDATE,
      )
    },
    changeToStage(stage = '') {
      this.newResource = 'Opportunity'
      this.newFormType = 'STAGE_GATING'
      this.newCustomForm = this.allForms.find(
        (f) =>
          f.resource == this.OPPORTUNITY && f.formType == this.STAGE_GATING && f.stage == stage,
      )
    },
    changeToContact() {
      this.newResource = 'Contact'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.CONTACT && f.formType == this.UPDATE,
      )
    },
    changeToLead() {
      this.newResource = 'Lead'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.LEAD && f.formType == this.UPDATE,
      )
    },
    switchFormType() {
      this.newFormType === 'CREATE' ? (this.newFormType = 'UPDATE') : (this.newFormType = 'CREATE')

      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.newResource && f.formType == this.newFormType,
      )
    },
    camelize(str) {
      return str[0] + str.slice(1).toLowerCase()
    },
    async goToProducts() {
      if (
        (this.resource == 'Opportunity' || this.resource == 'Account') &&
        this.customForm.formType == FORM_CONSTS.MEETING_REVIEW
      ) {
        if (!this.meetingType.length && !this.actionChoices.length) {
          this.$toast('Please enter a meeting type', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          return
        }
      }
      this.savingForm = true

      let fields = new Set([...this.addedFields.map((f) => f.id)])
      fields = Array.from(fields).filter((f) => !this.removedFields.map((f) => f.id).includes(f))
      let fields_ref = this.addedFields.filter((f) => fields.includes(f.id))

      SlackOAuth.api
        .postOrgCustomForm({
          ...this.customForm,
          fields: fields,
          removedFields: this.removedFields,
          fields_ref: fields_ref,
        })
        .then((res) => {
          this.$emit('update:selectedForm', res)
          this.$store.dispatch('refreshCurrentUser')
          this.$toast('Form added successfully', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        })
        .finally(() => {
          this.savingForm = false
          if (this.fromAdmin) {
            this.$router.go()
          } else {
            this.$router.push({ name: 'ProductForm' })
          }
        })
    },
    lowerCase(word1, word2) {
      return (word1 + ' ' + word2)
        .toLowerCase()
        .split(' ')
        .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
        .join(' ')
    },
    productSelect() {
      this.productSelected = !this.productSelected
    },
    getActionChoices() {
      this.loadingMeetingTypes = true
      const action = ActionChoice.api
        .list({})
        .then((res) => {
          this.actionChoices = res.results
        })
        .finally((this.loadingMeetingTypes = false))
    },
    async onFieldsNextPage() {
      this.dropdownLoading = true
      await this.formFields.addNextPage().then(() => {
        setTimeout(() => {
          this.dropdownLoading = false
        }, 1000)
      })
    },
    canRemoveField(field) {
      // If form is create required fields cannot be removed
      // if form is update required fields can be removed
      // if form is meeting review depening on the resource it can/cant be removed
      if (
        this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource] &&
        ~this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource].findIndex((f) => field.id == f)
      ) {
        return false
      } else {
        return true
      }
    },
    onAddField(field) {
      if (this.addedFieldIds.includes(field.id)) {
        this.canRemoveField(field) && this.onRemoveField(field)
        return
      }
      this.addedFields.push({ ...field, order: this.addedFields.length, includeInRecap: true })
      // this.formFields.filters = { salesforceObject: this.resource }
      // this.formFields.refresh()
    },
    goBack() {
      if (this.fromAdmin) {
        this.goBackAdmin()
      } else {
        this.$router.push({ name: 'Required' })
      }
    },
    goToUpdateOpp() {
      this.$router.push({ name: 'UpdateOpportunity' })
    },
    goToValidations() {
      this.$emit('cancel-selected')
    },
    onRemoveField(field) {
      // remove from the array if  it exists

      this.addedFields = [...this.addedFields.filter((f) => f.id != field.id)]

      // if it exists in the current fields add it to remove field

      if (~this.currentFields.findIndex((f) => f == field.id)) {
        this.removedFields = [this.removedFields, field]
      }
    },
    async onSave() {
      if (
        (this.newResource == 'Opportunity' || this.newResource == 'Account') &&
        this.newCustomForm.formType == FORM_CONSTS.MEETING_REVIEW
      ) {
        if (!this.meetingType.length && !this.actionChoices.length) {
          this.$toast('Please enter a meeting type', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          return
        }
      }
      this.savingForm = true

      let fields = new Set([...this.addedFields.map((f) => f.id)])
      fields = Array.from(fields).filter((f) => !this.removedFields.map((f) => f.id).includes(f))
      let fields_ref = this.addedFields.filter((f) => fields.includes(f.id))

      SlackOAuth.api
        .postOrgCustomForm({
          ...this.newCustomForm,
          fields: fields,
          removedFields: this.removedFields,
          fields_ref: fields_ref,
        })
        .then((res) => {
          // this.$emit('update:selectedForm', res)
          this.$router.go()
          this.$toast('Form saved', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        })
        .finally(() => {
          this.savingForm = false
          // if (this.formType !== 'STAGE_GATING' && !this.fromAdmin) {
          //   this.$router.push({ name: 'Required' })
          // } else {
          //   this.$router.go()
          // }
        })
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
@import '@/styles/buttons';

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
::v-deep .sortable-ghost {
  border: 1px dashed $very-light-gray;
  border-radius: 6px;
  padding-left: 8px;
}

.delete {
  background-color: white !important;
  border: 1px solid $coral !important;
  border-radius: 0.25rem;
  color: $coral !important;
  cursor: pointer;
  padding: 8px 16px;
  margin-right: 8px;
}
.red-text {
  color: $coral;
}
input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 0.9ex;
  left: 0.4ex;
  border: 2px solid $dark-green;
  border-top: none;
  border-right: none;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  transform: rotate(-45deg);
}

input[type='checkbox'] {
  line-height: 2.1ex;
}

input[type='checkbox'] {
  position: absolute;
  left: -999em;
}

input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

input[type='checkbox'] + label::before {
  content: '';
  display: inline-block;
  vertical-align: -22%;
  height: 1.75ex;
  width: 1.75ex;
  background-color: white;
  border: 1px solid rgb(182, 180, 180);
  border-radius: 4px;
  margin-right: 0.5em;
}
.form-type {
  padding: 6px 12px 6px 4px;
  img {
    padding-top: 2px;
  }
  transition: all 0.2s;
}
.form-type:hover {
  opacity: 0.8;
  cursor: pointer;
  border-radius: 6px;
  transform: translateY(-10%);
}
.search-bar {
  background-color: white;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border-radius: 8px;
  margin-top: 16px;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
input[type='search'] {
  width: 25vw;
  letter-spacing: 0.75px;
  border: none;
  padding: 4px;
  margin: 0;
}
::placeholder {
  color: $very-light-gray;
}
input[type='search']:focus {
  outline: none;
}
.field-section {
  width: 40vw;
  background-color: white;
  height: 98vh;
  margin-top: 16px;
  margin-left: 16px;
  padding: 0px 32px;
  border-radius: 6px;
  letter-spacing: 0.75px;
  &__title {
    letter-spacing: 0.75px;
  }
  &__fields {
    h4 {
      font-size: 13px;
      font-weight: 400;
      margin-bottom: 8px;
    }
    p {
      font-size: 12px;
      letter-spacing: 0.75px;
    }
    div {
      outline: 1px solid $soft-gray;
      border-radius: 6px;
      padding: 4px 16px;
      margin-top: 16px;

      section {
        span {
          color: $coral;
          margin-left: 4px;
        }
      }
    }
  }
}
.wrapper {
  width: 100%;
  margin: 0 auto;
  font-size: 14px;
  letter-spacing: 0.75px;
}
.tabs {
  position: relative;
  margin: 16px 0;
  background: white;
  border-radius: 6px;
}
.tabs::before,
.tabs::after {
  content: '';
  display: table;
}
.tabs::after {
  clear: both;
}
.tab {
  float: left;
}
.tab-switch {
  display: none;
}
.tab-label {
  position: relative;
  display: block;
  line-height: 2.75em;
  height: 3em;
  padding: 0 1.618em;
  color: $light-gray-blue;
  cursor: pointer;
  top: 0;
  transition: all 0.25s;
}
.tab-label:hover {
  top: -0.25rem;
  transition: top 0.25s;
}
.tab-content {
  width: 100%;
  height: 92vh;
  position: absolute;
  z-index: 1;
  top: 2.75em;
  left: 0;
  padding: 8px 24px;
  background: #fff;
  color: $base-gray;
  opacity: 0;
  transition: all 0.35s;
  overflow: scroll;
  border-radius: 6px;

  section {
  }
  &__div {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}
.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
#formSection {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  // border: 1px dashed $base-gray;
  padding-bottom: 32px;
  margin-top: 16px;
  border-radius: 0.3rem;
  height: 72vh;
  overflow: scroll;

  section {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    background-color: white;
    border-radius: 6px;
    min-height: 24vh;
    margin-top: 16px;
    width: 100%;
    padding: 0px 40px 0px 0px;

    input {
      width: 100%;
      border: 1px solid $soft-gray;
      border-radius: 0.3rem;
      background-color: white;
      min-height: 2.5rem;
      font-family: $base-font-family;
      margin-bottom: 16px;
      padding-left: 8px;
    }
    textarea {
      width: 100%;
      border: 1px solid $soft-gray;
      border-radius: 0.3rem;
      background-color: white;
      min-height: 2.5rem;
      font-family: $base-font-family;
      resize: none;
      padding-left: 8px;
    }
  }

  div {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    width: 99%;
    div {
      display: flex;
      flex-direction: row;
      align-items: flex-end;
      img {
        filter: invert(45%);
        margin: 0px 8px 8px 12px;
      }
    }
  }
}

// #formSection::-webkit-scrollbar {
//   width: 4px;
//   height: 0px;
// }
// #formSection::-webkit-scrollbar-thumb {
//   background-color: $soft-gray;
//   box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
//   border-radius: 0.3rem;
// }
// #formSection::-webkit-scrollbar-track {
//   box-shadow: inset 2px 2px 4px 0 $off-white;
//   border-radius: 0.3rem;
// }
// #formSection::-webkit-scrollbar-track-piece {
//   margin-top: 12px;
// }

#formField {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 4px 8px;
  border: 1px solid $soft-gray;
  border-radius: 0.3rem;
  background-color: white;
  font-family: $base-font-family;
  margin-top: 8px;
  cursor: grab;
  img {
    padding-top: 8px;
    cursor: grab;
  }
}
.tab-switch:checked + .tab-label {
  background: #fff;
  color: $base-gray;
  border-bottom: 0;
  transition: all 0.35s;
  z-index: 1;
  top: -0.0625rem;
}
.tab-switch:checked + label + .tab-content {
  z-index: 2;
  opacity: 1;
  transition: all 0.35s;
}
.tab-text {
  color: $light-gray-blue;
  font-size: 14px;
  letter-spacing: 0.75px;
}
//////END TAB STYLE//////

.sticky {
  top: 0;
  position: sticky;
  background-color: red;
  padding-top: 0px;
  margin-top: 0;
}

.card {
  &__header {
    display: flex;
    align-items: center;
    justify-content: center;
    img {
      margin: 0;
      padding: 0;
    }
  }
  &__img {
    background-color: white;
    border-radius: 100%;
    padding: 6px 8px 2px 4px;
    box-shadow: 1px 1px 1px $very-light-gray;
  }
}
.overlap {
  z-index: 2;
  margin-left: -12px;
  box-shadow: 1px 1px 0.5px 0.5px $very-light-gray;
  // background-color: white;
}
.extra-padding {
  padding: 5px 4px 3px 4px;
}
.section-title {
  letter-spacing: 0.5px;
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
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
.invert {
  filter: invert(80%);
  height: 1rem;
}
.invert2 {
  filter: invert(80%);
}
.img-border {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border: 1px solid #e8e8e8;
  border-radius: 0.2rem;
  cursor: pointer;
  padding: 0.15rem 0.3rem;
}
.label {
  font-size: 0.85rem;
}
.green {
  color: $dark-green;
  font-size: 0.85rem;
}
.default_button {
  padding: 0.5rem 1rem;
  margin-top: 0.5rem;
  border-radius: 0.2rem;
  border: none;
  cursor: pointer;
  color: $dark-green;
  background: white;

  img {
    height: 0.75rem;
    filter: invert(39%) sepia(96%) saturate(373%) hue-rotate(94deg) brightness(75%) contrast(94%);
  }
}
.recommend {
  position: absolute;
  bottom: 20vh;
  left: 34vw;
  z-index: 5;
  background-color: white;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
  box-shadow: 1px 2px 2px $very-light-gray;
  height: 40vh;
  width: 30vw;
  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid #e8e8e8;
    height: 4rem;
    padding: 1rem;

    letter-spacing: 0.5px;
    img {
      height: 1rem;
      filter: invert(30%);
    }
  }

  &__body {
    height: 5rem;
    display: flex;
    align-items: flex-start;
    justify-content: space-evenly;
    flex-direction: row;
    margin-top: -0.5rem;
    font-size: 14px;
    padding: 0.5rem;
  }
}
.drop {
  border: 2px solid $soft-gray;
  border-radius: 0.25rem;
  color: $very-light-gray;
  padding: 0.25rem 0.5rem;
  max-height: 2rem;
}
.invisible {
  visibility: hidden;
}
.white-background {
  background-color: white;
  border-radius: 0.25rem;
  height: 1.7rem;
  width: 1.7rem;
  margin-right: 0.25rem;
}
#drag {
  filter: invert(60%);
}
#remove {
  filter: invert(40%);
}
.drag-item {
  display: flex;
  flex-direction: row;
  align-items: center !important;
  border-radius: 0.2rem;
}
.center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
.centered {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: row;
}
.drag-section {
}
.header-img {
  padding: 5px 8px;
  border-radius: 4px;
  margin-left: 4px;
}
.active {
  background-color: $off-white;
  img {
    filter: invert(50%);
  }
}
.slack-form-builder {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  padding: 0rem;
  margin: 0;
  color: $base-gray;
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
.primary-button {
  padding: 0.4rem 1.5rem;
  box-shadow: none;
  font-weight: 400;
}
.primary-button:disabled {
  background-color: $soft-gray;
}
img:hover {
  cursor: pointer;
}
.close {
  padding: 0.5rem 1.5rem;
  background: transparent;
  color: $very-light-gray;
  border: 2px solid $soft-gray;
  border-radius: 0.25rem;
  opacity: 0.8;
}
.save {
  padding: 8px 20px;
  font-size: 13px;
  background-color: $dark-green;
  color: white;
  border: none;
  border-radius: 0.25rem;
  margin-right: 3vw;
  cursor: pointer;
}
.custom-object-button {
  padding: 8px 20px;
  font-size: 13px;
  background-color: $dark-green;
  color: white;
  border: none;
  border-radius: 0.25rem;
  margin-right: 8px;
  cursor: pointer;
}
.white_button {
  padding: 8px 20px;
  font-size: 14px;
  background-color: white;
  color: $base-gray;
  border: none;
  border-radius: 0.25rem;
  margin-right: 3vw;
  border: 1px solid $soft-gray;
  cursor: pointer;
}
:disabled {
  padding: 12px 20px;
  background-color: $soft-gray;
  color: $light-gray-blue;
  border: none;
  border-radius: 0.25rem;
  font-size: 13px;
  margin-left: 0.5rem;
  opacity: 0.8;
  cursor: text;
}
.disabled__ {
  background-color: transparent;
  font-size: 14px;
  color: $dark-green;
  border: none;
  letter-spacing: 1px;
  cursor: pointer;
}
.example--footer {
  position: sticky;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  margin-top: auto;
  bottom: 0;
  background-color: white;
  outline: 1px solid white;
  z-index: 2;
}
.example-text {
  position: absolute;
  bottom: 180px;
  left: 50px;
  opacity: 0.1;
  filter: alpha(opacity=50);
  font-size: 3.5rem;
  transform: rotate(-45deg);
}
.collection_fields {
  background-color: $white;
  padding: 4px 16px 0px 16px;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
  overflow: auto;
  height: 260px;
  width: 300px;
  display: flex;
  flex-direction: column;
  position: relative;
}
.stage_fields {
  background-color: $white;
  border-radius: 0.5rem;
  height: 74vh;
  width: 36vw;
  overflow-y: scroll;
  display: flex;
  flex-direction: column;
  position: relative;
  border: 1px solid #e8e8e8;
}
.opportunity__row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.row__ {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
}
.drop-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.opp-modal-container {
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  background-color: white;
  // width: 44vw;
  width: 70vw;
  height: 80vh;
  border-radius: 0.5rem;
  padding: 1rem;
  // border: 1px solid #e8e8e8;
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
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  letter-spacing: 1px;
  h4 {
    font-size: 20px;
  }
}
.logo {
  margin: 0px 8px 0px 16px;
  background-color: $white-green;
  border-radius: 4px;
  padding: 4px 6px;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
.modal-label {
  display: flex;
  align-items: flex-start;
  padding: 6px 0px;
  font-size: 12.5px;
  min-width: 80px;
  margin-top: 12px;
  letter-spacing: 1px;
  color: $light-gray-blue;
  border: none;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
.add-button {
  display: flex;
  align-items: center;
  border: none;
  margin: 0 0.5rem 0 0;
  padding: 9px 12px;
  font-size: 13px;
  border-radius: 6px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  letter-spacing: 0.75px;
}
.add-button:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.cancel {
  color: $dark-green;
  font-weight: bold;
  margin-left: 1rem;
  cursor: pointer;
}
</style>