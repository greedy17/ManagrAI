<template>
  <div @keyup.esc="closeInlineEditor" tabindex="0" class="pipelines">
    <Modal v-if="modalOpen" dimmed>
      <div class="modal-container rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" height="26px" alt="" />
            <h4>{{ selectedresourceName }} Notes</h4>
          </div>
          <div class="flex-row">
            <img
              @click="resetNotes"
              src="@/assets/images/close.svg"
              height="24px"
              alt=""
              style="margin-right: 16px; filter: invert(30%); cursor: pointer"
            />
          </div>
        </div>

        <div class="flex-row-spread-start">
          <div style="margin-top: 8px">
            <span class="input-container">
              <input
                class="input-field"
                placeholder="Note Title"
                type="text"
                v-model="noteTitle"
                @input=";(value = $event.target.value), setUpdateValues('meeting_type', value)"
              />
            </span>

            <span class="input-container">
              <div
                style="margin-top: -20px"
                @input="setUpdateValues('meeting_comments', $event.target.innerHTML)"
                class="divArea"
                v-html="noteValue"
                contenteditable="true"
              ></div>
              <!-- <span v-if="!formData['meeting_comments']" class="div-placeholder"
                >Type your note here</span
              > -->
            </span>
            <section v-if="!addingTemplate" class="note-templates">
              <span
                v-if="noteTemplates.length"
                @click="addingTemplate = !addingTemplate"
                class="note-templates__content"
              >
                <!-- <img
                  src="@/assets/images/add-document.svg"
                  height="18px"
                  style="margin-right: 2px"
                  alt=""
                /> -->
                Insert template
              </span>

              <span @click="goToNotes" class="note-templates__content" v-else>
                Create a template
                <img src="@/assets/images/note.svg" style="margin-left: 4px" height="18px" alt=""
              /></span>
            </section>

            <section class="note-templates2" v-else>
              <div
                v-for="(template, i) in noteTemplates"
                :key="i"
                @click="setTemplate(template.body, 'meeting_comments', template.subject)"
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

          <div class="note-container" v-if="notes.length">
            <section class="note-section" :key="i" v-for="(note, i) in notes">
              <p class="note-section__title">
                {{ note.saved_data__meeting_type ? note.saved_data__meeting_type : 'Untitled' }}
              </p>
              <p class="note-section__date">
                {{ weekDay(note.submission_date) }} {{ formatDateTime(note.submission_date) }}
              </p>
              <pre v-html="note.saved_data__meeting_comments" class="note-section__body"></pre>
            </section>
          </div>

          <div v-else class="note-container">
            <div class="empty-list">
              <section class="bg-img"></section>
              <h4>Nothing here</h4>
              <p>Start taking your notes in Managr.</p>
            </div>
          </div>
        </div>

        <footer class="modal-container__footer">
          <!-- <p>Total: {{ notesLength }}</p> -->
          <button @click="updateResource()" class="add-button">Save note</button>
        </footer>
      </div>
    </Modal>
    <Modal
      v-if="addOppModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetAddOpp()
        }
      "
    >
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row" @click="test(/*stageValidationFields*/stageGateField)">
            <img src="@/assets/images/logo.png" class="logo" height="26px" alt="" />
            <h3>{{userCRM === 'SALESFORCE' ? 'Create Opportunity' : 'Create Deal'}}</h3>
          </div>
          <img
            src="@/assets/images/close.svg"
            style="height: 1.25rem; margin-top: -1rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetAddOpp"
            alt=""
          />
        </div>
        <div class="opp-modal">
          <div>
            <section :key="field.id" v-for="field in createOppForm">
              <div
                v-if="
                  field.dataType === 'TextArea' ||
                  (field.dataType === 'String' && field.apiName === 'NextStep')
                "
              >
                <label class="label">{{ field.referenceDisplayLabel }}</label>
                <textarea
                  id="user-input"
                  cols="30"
                  rows="4"
                  :disabled="savingCreateForm"
                  style="width: 40.25vw; border-radius: 0.4rem"
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                >
                </textarea>
              </div>
              <div class="col" v-else-if="field.dataType === 'String'">
                <label class="label">{{ field.referenceDisplayLabel }}</label>
                <input
                  :disabled="savingCreateForm"
                  id="user-input"
                  type="text"
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                />
              </div>
              <div v-else-if="field.apiName === 'AccountId'">
                <label class="label">{{ field.referenceDisplayLabel }}</label>
                <Multiselect
                  v-model="selectedAccount"
                  :options="allAccounts"
                  @search-change="getAccounts($event)"
                  @select="setUpdateValues(field.apiName, $event.id, false)"
                  openDirection="below"
                  style="width: 40.25vw"
                  selectLabel="Enter"
                  track-by="id"
                  label="name"
                  :loading="dropdownLoading || loadingAccounts"
                >
                  <template v-slot:noResult>
                    <p class="multi-slot">No results.</p>
                  </template>
  
                  <template v-slot:placeholder>
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Account
                    </p>
                  </template>
                </Multiselect>
              </div>
              <div
                v-else-if="
                  field.apiName === 'dealstage' || field.apiName === 'Stage Name'
                "
              >
                <div v-if="savedPipeline">
                  <label class="label">{{ field.referenceDisplayLabel }}</label>
    
                  <Multiselect
                    v-model="currentVals[field.apiName]"
                    :options="
                      field.apiName === 'dealstage' ? field.options[0][savedPipeline.id].stages :
                      userCRM === 'HUBSPOT' && field.dataType !== 'Reference' ? field.options : 
                      (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
                        ? allPicklistOptions[field.id]
                        : createReferenceOpts[field.apiName]
                    "
                    @select="
                      setUpdateValues(
                        field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                        field.apiName === 'dealstage' ? $event.id :
                        (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && field.apiName !== 'dealstage'
                          ? $event.value
                          : $event.id,
                        field.dataType === 'MultiPicklist' ? true : false,
                      )
                    "
                    @open="
                      field.dataType === 'Reference'
                        ? getCreateReferenceOpts(field.apiName, field.id, field.options)
                        : null
                    "
                    @search-change="
                      field.dataType === 'Reference'
                        ? getReferenceFieldList(field.apiName, field.id, 'create1', field.options, $event)
                        : null
                    "
                    :multiple="field.dataType === 'MultiPicklist' ? true : false"
                    openDirection="below"
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
                    :loading="referenceLoading"
                  >
                    <template v-slot:noResult>
                      <p class="multi-slot">No results ? Try loading more</p>
                    </template>
                    <template v-slot:placeholder>
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        {{ `${field.referenceDisplayLabel}` }}
                      </p>
                    </template>
                  </Multiselect>
    
                  <div
                    :class="stageGateField ? 'adding-stage-gate' : 'hide'"
                    v-if="(field.apiName === 'StageName' || field.apiName === 'dealstage')"
                  >
                    <div class="adding-stage-gate__body">
                      <p>{{ stageGateField }} required</p>
                      <div v-for="(field, i) in stageValidationFields[stageGateField]" :key="i">
                        <div
                          v-if="
                            field.dataType === 'Picklist' ||
                            field.dataType === 'MultiPicklist' ||
                            (field.dataType === 'Reference' && field.apiName !== 'AccountId')
                          "
                        >
                          <label class="red-label">{{ field.referenceDisplayLabel }}:</label>
                          <Multiselect
                            :options="
                              (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
                                ? allPicklistOptions[field.id]
                                : stageReferenceOpts[field.apiName]
                                ? stageReferenceOpts[field.apiName]
                                : []
                            "
                            @select="
                              setUpdateValidationValues(
                                field.apiName === 'ForecastCategory'
                                  ? 'ForecastCategoryName'
                                  : field.apiName,
                                field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                                  ? $event.value
                                  : $event.id,
                              )
                            "
                            @open="
                              field.dataType === 'Reference'
                                ? getStageReferenceOpts(field.apiName, field.id)
                                : null
                            "
                            openDirection="below"
                            :loading="dropdownLoading"
                            v-model="dropdownVal[field.apiName]"
                            style="width: 40vw"
                            selectLabel="Enter"
                            :multiple="field.dataType === 'MultiPicklist' ? true : false"
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
                            <template v-slot:noResult>
                              <p class="multi-slot">No results.</p>
                            </template>
                            <template v-slot:placeholder>
                              <p class="slot-icon">
                                <img src="@/assets/images/search.svg" alt="" />
                                {{ field.apiName }}
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
                            <template v-slot:noResult>
                              <p class="multi-slot">No results.</p>
                            </template>
    
                            <template v-slot:placeholder>
                              <p class="slot-icon">
                                <img src="@/assets/images/search.svg" alt="" />
                                Accounts
                              </p>
                            </template>
                          </Multiselect>
                        </div>
                        <div v-else-if="field.dataType === 'String' && field.apiName !== 'NextStep'">
                          <label class="red-label"
                            >{{ field.referenceDisplayLabel }} <span>*</span></label
                          >
                          <input
                            id="user-input"
                            type="text"
                            :placeholder="currentVals[field.apiName]"
                            :disabled="savingCreateForm"
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
                          <label class="red-label"
                            >{{ field.referenceDisplayLabel }} <span>*</span></label
                          >
                          <textarea
                            id="user-input"
                            cols="30"
                            rows="2"
                            :disabled="savingCreateForm"
                            :placeholder="currentVals[field.apiName]"
                            style="width: 40.25vw; border-radius: 6px; padding: 7px"
                            v-model="currentVals[field.apiName]"
                            @input="
                              ;(value = $event.target.value),
                                setUpdateValidationValues(field.apiName, value)
                            "
                          >
                          </textarea>
                        </div>
                        <div v-else-if="field.dataType === 'Date'">
                          <label class="red-label"
                            >{{ field.referenceDisplayLabel }} <span>*</span></label
                          >
                          <input
                            type="text"
                            :disabled="savingCreateForm"
                            onfocus="(this.type='date')"
                            onblur="(this.type='text')"
                            :placeholder="currentVals[field.apiName]"
                            v-model="currentVals[field.apiName]"
                            id="user-input"
                            @input="
                              ;(value = $event.target.value),
                                setUpdateValidationValues(field.apiName, value)
                            "
                          />
                        </div>
                        <div v-else-if="field.dataType === 'DateTime'">
                          <label class="red-label"
                            >{{ field.referenceDisplayLabel }} <span>*</span></label
                          >
                          <input
                            type="datetime-local"
                            id="start"
                            :disabled="savingCreateForm"
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
                            field.dataType === 'Currency' ||
                            field.dataType === 'Int'
                          "
                        >
                          <label class="red-label"
                            >{{ field.referenceDisplayLabel }} <span>*</span></label
                          >
                          <input
                            id="user-input"
                            type="number"
                            :disabled="savingCreateForm"
                            v-model="currentVals[field.apiName]"
                            :placeholder="currentVals[field.apiName]"
                            @input="
                              ;(value = $event.target.value),
                                setUpdateValidationValues(field.apiName, value)
                            "
                          />
                        </div>
                        <div v-else-if="field.dataType === 'Boolean'">
                          <label class="red-label">{{ field.referenceDisplayLabel }}:</label>
    
                          <Multiselect
                            v-model="dropdownVal[field.apiName]"
                            :options="booleans"
                            @select="setUpdateValidationValues(field.apiName, $event)"
                            openDirection="below"
                            style="width: 40vw"
                            selectLabel="Enter"
                          >
                            <template v-slot:noResult>
                              <p class="multi-slot">No results.</p>
                            </template>
                            <template v-slot:placeholder>
                              <p class="slot-icon">
                                <img src="@/assets/images/search.svg" alt="" />
                                {{ currentVals[field.apiName] }}
                              </p>
                            </template>
                          </Multiselect>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else>
                  <label class="label">Select Pipeline for Stage</label>
                  <Multiselect
                    v-model="savedPipeline"
                    :options="pipelineOptions"
                    @open="getPipelineOptions(field.options[0])"
                    @select="setUpdateValues(field.apiName, field.apiName === 'dealstage' ? $event.id : $event.value)"
                    openDirection="below"
                    style="width: 40.25vw"
                    selectLabel="Enter"
                    track-by="id"
                    label="label"
                  >
                    <template v-slot:noResult>
                      <p class="multi-slot">No results.</p>
                    </template>
    
                    <template v-slot:placeholder>
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        Select Pipeline
                      </p>
                    </template>
                  </Multiselect>
                </div>
              </div>
              <div
                v-else-if="
                  field.dataType === 'Picklist' ||
                  field.dataType === 'MultiPicklist' ||
                  (field.dataType === 'Reference' && field.apiName !== 'AccountId')
                "
                
              >
                <label class="label" @click="test(field)">{{ field.referenceDisplayLabel }}</label>
  
                <Multiselect
                  v-model="currentVals[field.apiName]"
                  :options="
                    field.apiName === 'dealstage' ? field.options[0][savedOpp.secondary_data.pipeline].stages :
                    userCRM === 'HUBSPOT' && field.dataType !== 'Reference' ? field.options : 
                    (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
                      ? allPicklistOptions[field.id]
                      : createReferenceOpts[field.apiName]
                  "
                  @select="
                    setUpdateValues(
                      field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                      (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && field.apiName !== 'dealstage'
                        ? $event.value
                        : $event.id,
                      field.dataType === 'MultiPicklist' ? true : false,
                    )
                  "
                  @open="
                    field.dataType === 'Reference'
                      ? getCreateReferenceOpts(field.apiName, field.id, field.options)
                      : null
                  "
                  @search-change="
                    field.dataType === 'Reference'
                      ? getReferenceFieldList(field.apiName, field.id, 'create1', field.options, $event)
                      : null
                  "
                  :multiple="field.dataType === 'MultiPicklist' ? true : false"
                  openDirection="below"
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
                  :loading="referenceLoading"
                >
                  <template v-slot:noResult>
                    <p class="multi-slot">No results ? Try loading more</p>
                  </template>
                  <template v-slot:placeholder>
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      {{ `${field.referenceDisplayLabel}` }}
                    </p>
                  </template>
                </Multiselect>
  
                <div
                  :class="stageGateField ? 'adding-stage-gate' : 'hide'"
                  v-if="(field.apiName === 'StageName' || field.apiName === 'dealstage')"
                >
                  <div class="adding-stage-gate__body">
                    <p>{{ stageGateField }} required</p>
                    <div v-for="(field, i) in stageValidationFields[stageGateField]" :key="i">
                      <div
                        v-if="
                          field.dataType === 'Picklist' ||
                          field.dataType === 'MultiPicklist' ||
                          (field.dataType === 'Reference' && field.apiName !== 'AccountId')
                        "
                      >
                        <label class="red-label">{{ field.referenceDisplayLabel }}:</label>
                        <Multiselect
                          :options="
                            (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
                              ? allPicklistOptions[field.id]
                              : stageReferenceOpts[field.apiName]
                              ? stageReferenceOpts[field.apiName]
                              : []
                          "
                          @select="
                            setUpdateValidationValues(
                              field.apiName === 'ForecastCategory'
                                ? 'ForecastCategoryName'
                                : field.apiName,
                              field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                                ? $event.value
                                : $event.id,
                            )
                          "
                          @open="
                            field.dataType === 'Reference'
                              ? getStageReferenceOpts(field.apiName, field.id)
                              : null
                          "
                          openDirection="below"
                          :loading="dropdownLoading"
                          v-model="dropdownVal[field.apiName]"
                          style="width: 40vw"
                          selectLabel="Enter"
                          :multiple="field.dataType === 'MultiPicklist' ? true : false"
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
                          <template v-slot:noResult>
                            <p class="multi-slot">No results.</p>
                          </template>
                          <template v-slot:placeholder>
                            <p class="slot-icon">
                              <img src="@/assets/images/search.svg" alt="" />
                              {{ field.apiName }}
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
                          <template v-slot:noResult>
                            <p class="multi-slot">No results.</p>
                          </template>
  
                          <template v-slot:placeholder>
                            <p class="slot-icon">
                              <img src="@/assets/images/search.svg" alt="" />
                              Accounts
                            </p>
                          </template>
                        </Multiselect>
                      </div>
                      <div v-else-if="field.dataType === 'String' && field.apiName !== 'NextStep'">
                        <label class="red-label"
                          >{{ field.referenceDisplayLabel }} <span>*</span></label
                        >
                        <input
                          id="user-input"
                          type="text"
                          :placeholder="currentVals[field.apiName]"
                          :disabled="savingCreateForm"
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
                        <label class="red-label"
                          >{{ field.referenceDisplayLabel }} <span>*</span></label
                        >
                        <textarea
                          id="user-input"
                          cols="30"
                          rows="2"
                          :disabled="savingCreateForm"
                          :placeholder="currentVals[field.apiName]"
                          style="width: 40.25vw; border-radius: 6px; padding: 7px"
                          v-model="currentVals[field.apiName]"
                          @input="
                            ;(value = $event.target.value),
                              setUpdateValidationValues(field.apiName, value)
                          "
                        >
                        </textarea>
                      </div>
                      <div v-else-if="field.dataType === 'Date'">
                        <label class="red-label"
                          >{{ field.referenceDisplayLabel }} <span>*</span></label
                        >
                        <input
                          type="text"
                          :disabled="savingCreateForm"
                          onfocus="(this.type='date')"
                          onblur="(this.type='text')"
                          :placeholder="currentVals[field.apiName]"
                          v-model="currentVals[field.apiName]"
                          id="user-input"
                          @input="
                            ;(value = $event.target.value),
                              setUpdateValidationValues(field.apiName, value)
                          "
                        />
                      </div>
                      <div v-else-if="field.dataType === 'DateTime'">
                        <label class="red-label"
                          >{{ field.referenceDisplayLabel }} <span>*</span></label
                        >
                        <input
                          type="datetime-local"
                          id="start"
                          :disabled="savingCreateForm"
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
                          field.dataType === 'Currency' ||
                          field.dataType === 'Int'
                        "
                      >
                        <label class="red-label"
                          >{{ field.referenceDisplayLabel }} <span>*</span></label
                        >
                        <input
                          id="user-input"
                          type="number"
                          :disabled="savingCreateForm"
                          v-model="currentVals[field.apiName]"
                          :placeholder="currentVals[field.apiName]"
                          @input="
                            ;(value = $event.target.value),
                              setUpdateValidationValues(field.apiName, value)
                          "
                        />
                      </div>
                      <div v-else-if="field.dataType === 'Boolean'">
                        <label class="red-label">{{ field.referenceDisplayLabel }}:</label>
  
                        <Multiselect
                          v-model="dropdownVal[field.apiName]"
                          :options="booleans"
                          @select="setUpdateValidationValues(field.apiName, $event)"
                          openDirection="below"
                          style="width: 40vw"
                          selectLabel="Enter"
                        >
                          <template v-slot:noResult>
                            <p class="multi-slot">No results.</p>
                          </template>
                          <template v-slot:placeholder>
                            <p class="slot-icon">
                              <img src="@/assets/images/search.svg" alt="" />
                              {{ currentVals[field.apiName] }}
                            </p>
                          </template>
                        </Multiselect>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col" v-else-if="field.dataType === 'Date'">
                <label class="label">{{ field.referenceDisplayLabel }}</label>
                <input
                  type="date"
                  id="user-input"
                  :disabled="savingCreateForm"
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                />
              </div>
              <div class="col" v-else-if="field.dataType === 'DateTime'">
                <label class="label">
                  {{ field.referenceDisplayLabel }}
                </label>
                <input
                  type="datetime-local"
                  id="start"
                  :disabled="savingCreateForm"
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                />
              </div>
              <div
                v-else-if="
                  field.dataType === 'Phone' ||
                  field.dataType === 'Double' ||
                  field.dataType === 'Currency' ||
                  field.dataType === 'Int'
                "
                class="col"
              >
                <label class="label">{{ field.referenceDisplayLabel }}</label>
                <input
                  id="user-input"
                  type="number"
                  :disabled="savingCreateForm"
                  @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                />
              </div>
              <div v-else-if="field.dataType === 'Boolean'">
                <label class="label">{{ field.referenceDisplayLabel }}</label>
  
                <Multiselect
                  v-model="dropdownVal[field.apiName]"
                  :options="booleans"
                  @select="setUpdateValues(field.apiName, $event)"
                  openDirection="below"
                  style="width: 40.25vw"
                  selectLabel="Enter"
                >
                  <template v-slot:noResult>
                    <p class="multi-slot">No results.</p>
                  </template>
                  <template v-slot:placeholder>
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      {{ currentVals[field.apiName] }}
                    </p>
                  </template>
                </Multiselect>
              </div>
            </section>
            <div ref="product" class="adding-product" v-if="addingProduct">
              <!-- <img class="fullInvert" src="@/assets/images/tag.svg" alt="" /> -->
              <!-- <h3 style="color: #41b883">Add Product</h3> -->
  
              <div class="adding-product__body">
                <div>
                  <p>Pricebook:</p>
                  <Multiselect
                    @select="getPricebookEntries($event.integration_id)"
                    :options="pricebooks"
                    openDirection="below"
                    v-model="selectedPriceBook"
                    style="width: 40vw"
                    selectLabel="Enter"
                    label="name"
                  >
                    <template v-slot:placeholder>
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
                    <p>
                      {{
                        field.referenceDisplayLabel === 'PricebookEntry'
                          ? 'Products'
                          : field.referenceDisplayLabel
                      }}:
                    </p>
                    <Multiselect
                      :options="
                        (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
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
                      @open="
                        field.dataType === 'Reference'
                          ? getProductReferenceOpts(field.apiName, field.id)
                          : null
                      "
                      :loading="loadingProducts"
                      openDirection="below"
                      v-model="dropdownVal[field.apiName]"
                      style="width: 40vw"
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
                      <template v-slot:noResult>
                        <p class="multi-slot">No results. Try loading more</p>
                      </template>
                      <template v-slot:afterList>
                        <p v-if="showLoadMore" @click="loadMore" class="multi-slot__more">
                          Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                        </p>
                      </template>
                      <template v-slot:placeholder>
                        <p class="slot-icon">
                          <img src="@/assets/images/search.svg" alt="" />
                          {{ field.referenceDisplayLabel }}
                        </p>
                      </template>
                    </Multiselect>
                  </div>
  
                  <div class="col" v-else-if="field.dataType === 'String'">
                    <p>{{ field.referenceDisplayLabel }}</p>
                    <input
                      id="user-input"
                      type="text"
                      style="width: 40vw"
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
                    <p>{{ field.referenceDisplayLabel }}</p>
                    <textarea
                      id="user-input"
                      ccols="30"
                      rows="2"
                      :disabled="savingCreateForm"
                      :placeholder="currentVals[field.apiName]"
                      style="width: 40.25vw; border-radius: 6px; padding: 7px"
                      v-model="currentVals[field.apiName]"
                      @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                    >
                    </textarea>
                  </div>
                  <div class="col" v-else-if="field.dataType === 'Date'">
                    <p>{{ field.referenceDisplayLabel }}</p>
                    <input
                      type="text"
                      onfocus="(this.type='date')"
                      onblur="(this.type='text')"
                      style="width: 40vw"
                      :disabled="savingCreateForm"
                      :placeholder="currentVals[field.apiName]"
                      v-model="currentVals[field.apiName]"
                      id="user-input"
                      @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                    />
                  </div>
                  <div class="col" v-else-if="field.dataType === 'DateTime'">
                    <p>{{ field.referenceDisplayLabel }}</p>
                    <input
                      type="datetime-local"
                      id="start"
                      style="width: 40vw"
                      :disabled="savingCreateForm"
                      v-model="currentVals[field.apiName]"
                      @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                    />
                  </div>
                  <div
                    class="col"
                    v-else-if="
                      field.dataType === 'Phone' ||
                      field.dataType === 'Double' ||
                      field.dataType === 'Currency' ||
                      field.dataType === 'Int'
                    "
                  >
                    <p>{{ field.referenceDisplayLabel }}</p>
                    <input
                      id="user-input"
                      type="number"
                      style="width: 40vw"
                      :disabled="savingCreateForm"
                      v-model="currentVals[field.apiName]"
                      :placeholder="currentVals[field.apiName]"
                      @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="flex-end-opp">
          <div v-if="(hasProducts && userCRM === 'SALESFORCE')">
            <button
              v-if="(!addingProduct)"
              @click="addProduct"
              style="margin-bottom: 0.75rem"
              class="select-btn1"
              :disabled="savingCreateForm"
            >
              Add Product
            </button>

            <p @click="addProduct" v-else class="product-text">
              Adding product <img height="20px" src="@/assets/images/remove.svg" alt="" />
            </p>
          </div>
          <div v-else></div>

          <div v-if="!savingCreateForm" style="display: flex; align-items: center">
            <button class="add-button" @click="createResource(addingProduct ? true : false)">
              {{userCRM === 'SALESFORCE' ? 'Create Opportunity' : 'Create Deal'}}
            </button>
          </div>
          <div v-else>
            <PipelineLoader />
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="editOpModalOpen" dimmed>
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <span class="logo">
              <img src="@/assets/images/logo.png" height="24px" alt="" />
            </span>

            <h3>Update {{userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal'}}</h3>
          </div>
          <img
            src="@/assets/images/close.svg"
            style="height: 1.5rem; margin-top: -1.5rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetEdit"
            alt=""
          />
        </div>
        <div class="opp-modal">
          <section :key="i" v-for="(field, i) in oppFormCopy">
            <div
              style="margin-left: -0.5rem; margin-top: -2rem; display: none"
              v-if="field.apiName === 'meeting_type'"
            ></div>
            <div
              style="position: relative; display: none"
              v-else-if="field.apiName === 'meeting_comments'"
            ></div>
            <div
              v-else-if="
                field.dataType === 'TextArea' || (field.length > 250 && field.dataType === 'String')
              "
              class="col"
            >
              <label class="label">{{ field.referenceDisplayLabel }}</label>
              <textarea
                id="user-input"
                ccols="30"
                rows="4"
                :placeholder="currentVals[field.apiName]"
                style="width: 40.25vw; border-radius: 0.4rem; padding: 7px; resize: none"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div
              v-else-if="
                (field.dataType === 'String' && field.apiName !== 'meeting_type') ||
                (field.dataType === 'String' && field.apiName !== 'meeting_comments') ||
                (field.dataType === 'String' && field.apiName !== 'NextStep')
              "
              class="col"
            >
              <label class="label">{{ field.referenceDisplayLabel }}</label>
              <input
                id="user-input"
                type="text"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'Boolean'">
              <label class="label">{{ field.referenceDisplayLabel }}</label>
              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="booleans"
                @select="setUpdateValues(field.apiName, $event)"
                openDirection="below"
                style="width: 40.25vw"
                selectLabel="Enter"
              >
                <template v-slot:noResult>
                  <p class="multi-slot">No results.</p>
                </template>
                <template v-slot:placeholder>
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{ currentVals[field.apiName] }}
                  </p>
                </template>
              </Multiselect>
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
                <template v-slot:noResult>
                  <p class="multi-slot">No results.</p>
                </template>

                <template v-slot:placeholder>
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
                (field.dataType === 'Reference' && field.apiName !== 'AccountId')
              "
            >
              <label class="label">{{ field.referenceDisplayLabel }}</label>
              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="
                  field.apiName === 'dealstage' ? field.options[0][savedOpp.secondary_data.pipeline].stages :
                  userCRM === 'HUBSPOT' && field.dataType !== 'Reference' ? field.options : 
                  (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
                    ? allPicklistOptions[field.id]
                    : referenceOpts[field.apiName]
                "
                @select="
                  setUpdateValues(
                    field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                    field.apiName === 'dealstage' ? $event.id :
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? $event.value
                      : $event.id,
                    field.dataType === 'MultiPicklist' ? true : false,
                  )
                "
                @search-change="
                  field.dataType === 'Reference'
                    ? getReferenceFieldList(field.apiName, field.id, 'update', field.options, $event)
                    : null
                "
                @open="
                  field.dataType === 'Reference' ? getReferenceOpts(field.apiName, field.id, field.options) : null
                "
                :loading="dropdownLoading"
                openDirection="below"
                style="width: 40.25vw"
                selectLabel="Enter"
                :multiple="field.dataType === 'MultiPicklist' ? true : false"
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
                <template v-slot:noResult>
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template v-slot:placeholder>
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{
                      field.apiName === 'dealstage' ? field.options[0][savedOpp['secondary_data'].pipeline].stages.filter(stage => stage.id === savedOpp['secondary_data'][field.apiName])[0].label :
                        field.apiName === 'AccountId'
                          ? currentAccount
                          : field.apiName === 'OwnerId'
                          ? currentOwner
                          : currentVals && `${currentVals[field.apiName]}` !== 'null'
                          ? `${currentVals[field.apiName]}`
                          : `${field.referenceDisplayLabel}`
                    }}
                  </p>
                </template>
              </Multiselect>
              <div
                ref="primaryStageForm"
                :class="stageGateField ? 'adding-stage-gate' : 'hide'"
                v-if="field.apiName === 'StageName' || field.apiName === 'dealstage'"
              >
                <div class="adding-stage-gate__body">
                  <!-- <h4 style="color: #fa646a; font-size: 16px">
                    Fields required for moving to
                    <span style="background-color: #ffd4d4; padding: 4px; border-radius: 4px">{{
                      stageGateField
                    }}</span>
                  </h4> -->
                  <div v-for="(field, i) in stageValidationFields[stageGateField]" :key="i">
                    <div
                      v-if="
                        field.dataType === 'Picklist' ||
                        field.dataType === 'MultiPicklist' ||
                        (field.dataType === 'Reference' && field.apiName !== 'AccountId')
                      "
                    >
                      <label class="red-label">{{ field.referenceDisplayLabel }}:</label>
                      <Multiselect
                        :options="
                          (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
                            ? allPicklistOptions[field.id]
                            : stageReferenceOpts[field.apiName]
                            ? stageReferenceOpts[field.apiName]
                            : []
                        "
                        @select="
                          setUpdateValidationValues(
                            field.apiName === 'ForecastCategory'
                              ? 'ForecastCategoryName'
                              : field.apiName,
                            field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                              ? $event.value
                              : $event.id,
                          )
                        "
                        @open="
                          field.dataType === 'Reference'
                            ? getStageReferenceOpts(field.apiName, field.id)
                            : null
                        "
                        openDirection="below"
                        :loading="dropdownLoading"
                        v-model="dropdownVal[field.apiName]"
                        style="width: 40vw; margin-top: 8px"
                        selectLabel="Enter"
                        :multiple="field.dataType === 'MultiPicklist' ? true : false"
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
                        <template v-slot:noResult>
                          <p class="multi-slot">No results.</p>
                        </template>
                        <template v-slot:placeholder>
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
                    <div v-else-if="field.apiName === 'AccountId'">
                      <label class="red-label">{{ field.referenceDisplayLabel }}*</label>
                      <Multiselect
                        v-model="selectedAccount"
                        :options="allAccounts"
                        @search-change="getAccounts($event)"
                        @select="setUpdateValidationValues(field.apiName, $event.id)"
                        openDirection="below"
                        style="width: 40.25vw; margin-top: 8px"
                        selectLabel="Enter"
                        track-by="integration_id"
                        label="name"
                        :loading="dropdownLoading || loadingAccounts"
                      >
                        <template v-slot:noResult>
                          <p class="multi-slot">No results.</p>
                        </template>

                        <template v-slot:placeholder>
                          <p class="slot-icon">
                            <img src="@/assets/images/search.svg" alt="" />
                            {{ currentAccount }}
                          </p>
                        </template>
                      </Multiselect>
                    </div>
                    <div v-else-if="field.dataType === 'String' && field.apiName !== 'NextStep'">
                      <label class="red-label"
                        >{{ field.referenceDisplayLabel }} <span>*</span></label
                      >
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
                      <label class="red-label"
                        >{{ field.referenceDisplayLabel }} <span>*</span></label
                      >
                      <textarea
                        id="user-input"
                        ccols="30"
                        rows="2"
                        :placeholder="currentVals[field.apiName]"
                        style="width: 40.25vw; border-radius: 6px; padding: 7px"
                        v-model="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      >
                      </textarea>
                    </div>
                    <div v-else-if="field.dataType === 'Date'">
                      <label class="red-label"
                        >{{ field.referenceDisplayLabel }} <span>*</span></label
                      >
                      <input
                        type="text"
                        onfocus="(this.type='date')"
                        onblur="(this.type='text')"
                        :placeholder="currentVals[field.apiName]"
                        v-model="currentVals[field.apiName]"
                        id="user-input"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>
                    <div v-else-if="field.dataType === 'DateTime'">
                      <label class="red-label"
                        >{{ field.referenceDisplayLabel }} <span>*</span></label
                      >
                      <input
                        type="datetime-local"
                        id="start"
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
                        field.dataType === 'Currency' ||
                        field.dataType === 'Int'
                      "
                    >
                      <label class="red-label"
                        >{{ field.referenceDisplayLabel }} <span>*</span></label
                      >
                      <input
                        id="user-input"
                        type="number"
                        v-model="currentVals[field.apiName]"
                        :placeholder="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      />
                    </div>
                    <div v-else-if="field.dataType === 'Boolean'">
                      <label class="red-label">{{ field.referenceDisplayLabel }}:</label>

                      <Multiselect
                        v-model="dropdownVal[field.apiName]"
                        :options="booleans"
                        @select="setUpdateValidationValues(field.apiName, $event)"
                        openDirection="below"
                        style="width: 40.25vw"
                        selectLabel="Enter"
                      >
                        <template v-slot:noResult>
                          <p class="multi-slot">No results.</p>
                        </template>
                        <template v-slot:placeholder>
                          <p class="slot-icon">
                            <img src="@/assets/images/search.svg" alt="" />
                            {{ currentVals[field.apiName] }}
                          </p>
                        </template>
                      </Multiselect>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col" v-else-if="field.dataType === 'Date'">
              <label class="label">{{ field.referenceDisplayLabel }}</label>
              <input
                type="text"
                onfocus="(this.type='date')"
                onblur="(this.type='text')"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                id="user-input"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div class="col" v-else-if="field.dataType === 'DateTime'">
              <label class="label">{{ field.referenceDisplayLabel }}</label>
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
                field.dataType === 'Currency' ||
                field.dataType === 'Int'
              "
            >
              <label class="label">{{ field.referenceDisplayLabel }}</label>
              <input
                id="user-input"
                type="number"
                v-model="currentVals[field.apiName]"
                :placeholder="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
          </section>

          <div ref="product" class="adding-product" v-if="addingProduct">
            <!-- <img class="fullInvert" src="@/assets/images/tag.svg" alt="" /> -->
            <!-- <h4 style="color: #41b883">Add Product</h4> -->

            <div class="adding-product__body">
              <div v-if="!pricebookId">
                <p>Pricebook:</p>
                <Multiselect
                  @select="getPricebookEntries($event.integration_id)"
                  :options="pricebooks ? pricebooks : []"
                  openDirection="below"
                  v-model="selectedPriceBook"
                  style="width: 40vw"
                  selectLabel="Enter"
                  label="name"
                >
                  <template v-slot:placeholder>
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
                    (field.dataType === 'Reference' && field.apiName !== 'AccountId')
                  "
                >
                  <p>
                    {{
                      field.referenceDisplayLabel === 'PricebookEntry'
                        ? 'Products'
                        : field.referenceDisplayLabel
                    }}:
                  </p>
                  <Multiselect
                    :options="
                      (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
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
                    @open="
                      field.dataType === 'Reference'
                        ? getProductReferenceOpts(field.apiName, field.id)
                        : null
                    "
                    openDirection="below"
                    v-model="dropdownVal[field.apiName]"
                    style="width: 40vw"
                    selectLabel="Enter"
                    :track-by="
                      field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                        ? 'value'
                        : 'id'
                    "
                    :loading="loadingProducts"
                    :label="
                      field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                        ? 'label'
                        : 'name'
                    "
                  >
                    <template v-slot:noResult>
                      <p class="multi-slot">No results. Try loading more</p>
                    </template>
                    <template v-slot:afterList>
                      <p v-if="showLoadMore" @click="loadMore" class="multi-slot__more">
                        Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                      </p>
                    </template>
                    <template v-slot:placeholder>
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        {{ field.referenceDisplayLabel }}
                      </p>
                    </template>
                  </Multiselect>
                </div>

                <div v-else-if="field.dataType === 'String'">
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <input
                    id="user-input"
                    type="text"
                    style="width: 40vw"
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
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <textarea
                    id="user-input"
                    ccols="30"
                    rows="2"
                    :placeholder="currentVals[field.apiName]"
                    style="width: 40.25vw; border-radius: 6px; padding: 7px"
                    v-model="currentVals[field.apiName]"
                    @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                  >
                  </textarea>
                </div>
                <div v-else-if="field.dataType === 'Date'">
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <input
                    type="text"
                    onfocus="(this.type='date')"
                    onblur="(this.type='text')"
                    :placeholder="currentVals[field.apiName]"
                    style="width: 40vw"
                    v-model="currentVals[field.apiName]"
                    id="user-input"
                    @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                  />
                </div>
                <div v-else-if="field.dataType === 'DateTime'">
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <input
                    type="datetime-local"
                    id="start"
                    style="width: 40vw"
                    v-model="currentVals[field.apiName]"
                    @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                  />
                </div>
                <div
                  v-else-if="
                    field.dataType === 'Phone' ||
                    field.dataType === 'Double' ||
                    field.dataType === 'Currency' ||
                    field.dataType === 'Int'
                  "
                >
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <input
                    id="user-input"
                    style="width: 40vw"
                    type="number"
                    v-model="currentVals[field.apiName]"
                    :placeholder="currentVals[field.apiName]"
                    @input=";(value = $event.target.value), setCreateValues(field.apiName, value)"
                  />
                </div>
              </div>
            </div>
          </div>
          <div v-if="hasProducts && currentProducts && currentProducts.length">
            <section ref="allProducts" v-if="!editingProduct && viewingProducts">
              <div class="current-products" v-for="(product, i) in currentProducts" :key="i">
                <h4>
                  {{ product.secondary_data.Name }}
                </h4>
                <p>Quantity: {{ product.secondary_data.Quantity }}</p>
                <span
                  ><p>Total Price: ${{ product.secondary_data.TotalPrice }}</p>
                  <button
                    @click="
                      editProduct(
                        product.secondary_data.Id,
                        product.id,
                        product.name,
                        product.secondary_data,
                      )
                    "
                  >
                    <img src="@/assets/images/edit.svg" height="16px" alt="" />
                  </button>
                </span>
              </div>
            </section>

            <div class="current-products" v-if="editingProduct">
              <p style="color: #41b883; font-size: 15px; margin-bottom: 24px">
                {{ productName }}
              </p>
              <PipelineLoader v-if="savingProduct" />
              <div v-for="(field, i) in createProductForm" :key="i">
                <div
                  v-if="
                    field.dataType === 'Picklist' ||
                    field.dataType === 'MultiPicklist' ||
                    (field.dataType === 'Reference' && field.apiName !== 'AccountId')
                  "
                >
                  <p>
                    {{
                      field.referenceDisplayLabel === 'PricebookEntry'
                        ? 'Products'
                        : field.referenceDisplayLabel
                    }}
                  </p>
                  <Multiselect
                    :options="
                      (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
                        ? allPicklistOptions[field.id]
                        : productReferenceOpts[field.apiName]
                    "
                    @select="
                      setProductValues(
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
                    @open="
                      field.dataType === 'Reference'
                        ? getProductReferenceOpts(field.apiName, field.id)
                        : null
                    "
                    openDirection="below"
                    v-model="dropdownProductVal[field.apiName]"
                    style="width: 38vw"
                    selectLabel="Enter"
                    :track-by="
                      field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                        ? 'value'
                        : 'id'
                    "
                    :loading="loadingProducts"
                    :label="
                      field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                        ? 'label'
                        : 'name'
                    "
                  >
                    <template v-slot:noResult>
                      <p class="multi-slot">No results. Try loading more</p>
                    </template>
                    <template v-slot:afterList>
                      <p v-if="showLoadMore" @click="loadMore" class="multi-slot__more">
                        Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                      </p>
                    </template>
                    <template v-slot:placeholder>
                      <small class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        {{ field.referenceDisplayLabel }}
                      </small>
                    </template>
                  </Multiselect>
                </div>

                <div v-else-if="field.dataType === 'String'">
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <input
                    id="user-input"
                    type="text"
                    style="width: 38vw"
                    :placeholder="currentSelectedProduct[field.apiName]"
                    v-model="dropdownProductVal[field.apiName]"
                    @input=";(value = $event.target.value), setProductValues(field.apiName, value)"
                  />
                </div>

                <div
                  v-else-if="
                    field.dataType === 'TextArea' ||
                    (field.length > 250 && field.dataType === 'String')
                  "
                >
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <textarea
                    id="user-input"
                    ccols="30"
                    rows="2"
                    :placeholder="currentSelectedProduct[field.apiName]"
                    style="width: 38vw; border-radius: 6px; padding: 7px"
                    v-model="dropdownProductVal[field.apiName]"
                    @input=";(value = $event.target.value), setProductValues(field.apiName, value)"
                  >
                  </textarea>
                </div>
                <div v-else-if="field.dataType === 'Date'">
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <input
                    type="text"
                    onfocus="(this.type='date')"
                    onblur="(this.type='text')"
                    :placeholder="currentSelectedProduct[field.apiName]"
                    style="width: 38vw"
                    v-model="dropdownProductVal[field.apiName]"
                    id="user-input"
                    @input=";(value = $event.target.value), setProductValues(field.apiName, value)"
                  />
                </div>
                <div v-else-if="field.dataType === 'DateTime'">
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <input
                    type="datetime-local"
                    id="start"
                    style="width: 38vw"
                    :placeholder="currentSelectedProduct[field.apiName]"
                    v-model="dropdownProductVal[field.apiName]"
                    @input=";(value = $event.target.value), setProductValues(field.apiName, value)"
                  />
                </div>
                <div
                  v-else-if="
                    field.dataType === 'Phone' ||
                    field.dataType === 'Double' ||
                    field.dataType === 'Currency' ||
                    field.dataType === 'Int'
                  "
                >
                  <p>{{ field.referenceDisplayLabel }}</p>
                  <input
                    id="user-input"
                    style="width: 38vw"
                    type="number"
                    v-model="dropdownProductVal[field.apiName]"
                    :placeholder="currentSelectedProduct[field.apiName]"
                    @input=";(value = $event.target.value), setProductValues(field.apiName, value)"
                  />
                </div>
              </div>

              <div class="current-products__footer">
                <p @click="cancelEditProduct">Cancel</p>
                <button class="add-button__" @click="updateProduct">Update Product</button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex-end-opp">
          <div v-if="hasProducts && userCRM === 'SALESFORCE'" class="row">
            <button
              style="padding: 10px; margin-right: 4px"
              v-if="!addingProduct"
              @click="addProduct"
              class="select-btn1"
            >
              Add Product
            </button>

            <button @click="addProduct" v-else class="cancel" style="margin-right: 4px">
              Cancel
            </button>
            <button
              v-if="!viewingProducts && currentProducts && currentProducts.length"
              @click="toggleViewingProducts()"
              style="margin-left: 8px"
              class="select-btn1"
            >
              View products <span>{{ currentProducts ? currentProducts.length : 0 }}</span>
            </button>
            <button v-else-if="viewingProducts" @click="toggleViewingProducts()" class="cancel">
              Close products
            </button>
          </div>

          <div v-else></div>

          <div style="display: flex; align-items: center">
            <button
              style="padding: 10px"
              @click="
                updateResource()
                createProduct()
              "
              class="add-button__"
            >
              Update
            </button>
            <!-- <p @click="resetEdit" class="cancel">Cancel</p> -->
          </div>
        </div>
      </div>
    </Modal>

    <div ref="pipelines" v-if="!loading">
      <!-- <h3 class="pipeline-header">
        {{ !currentWorkflowName ? currentList : currentWorkflowName }}
      </h3> -->
      <section style="margin-top: -10px" class="flex-row-spread">
        <div v-if="/*!workflowCheckList.length && !primaryCheckList.length*/true" class="flex-row">
          <small class="pipeline-header">View:</small>
          <button @click.stop="showList = !showList" class="text-button" style="cursor: pointer">
            {{ !currentWorkflowName ? currentList : currentWorkflowName }}
            <span style="margin-left: 2px" class="green">{{
              selectedWorkflow && currentWorkflow ? currentWorkflow.length : allOpps.length
            }}</span>

            <img height="12px" src="@/assets/images/downArrow.svg" alt="" />
          </button>
          <div v-outside-click="closeListSelect" v-show="showList" class="list-section">
            <div class="list-section__title flex-row-spread">
              <p>{{userCRM === 'SALESFORCE' ? 'Opportunities' : 'Deals'}}</p>
            </div>
            <!-- <p @click="showPopularList = !showPopularList" class="list-section__sub-title">
              Standard Lists
              <img
                v-if="showPopularList"
                class="invert"
                src="@/assets/images/downArrow.svg"
                alt=""
              /><img v-else src="@/assets/images/rightArrow.svg" class="invert" alt="" />
            </p> -->
            <router-link style="width: 100%" v-bind:to="'/pipelines/'">
              <button @click="allOpportunities" class="list-button">
                All {{this.userCRM === 'SALESFORCE' ? 'Opportunities' : 'Deals'}}
                <span class="green">
                  {{ allOpps.length }}
                </span>
              </button>
            </router-link>
            <!-- <button v-if="!selectedWorkflow" @click="closeDatesThisMonth" class="list-button">
              Closing this month
              <span
                class="filter"
                v-if="currentList === 'Closing this month' && !currentWorkflowName"
              >
                active</span
              >
            </button> -->
            <!-- <button v-if="!selectedWorkflow" @click="closeDatesNextMonth" class="list-button">
              Closing next month
              <span
                class="filter"
                v-if="currentList === 'Closing next month' && !currentWorkflowName"
              >
                active</span
              >
            </button> -->
            <button
              @click="goToWorkflow(template.id)"
              class="list-button"
              v-for="template in templates.list"
              :key="template.id"
            >
              {{ template.title }} <span class="green">{{ template.sobjectInstances.length }}</span>
            </button>
          </div>
          <div
            v-for="(filter, i) in activeFilters"
            :key="i"
            @mouseenter="hoveredIndex = i"
            @mouseleave="hoveredIndex = null"
            class="main"
          >
            <strong style="font-size: 14px">{{ filter }}</strong>
            <small style="font-weight: 400px; margin-left: 0.2rem">{{ setFilters[i][0] }}</small>
            <small style="margin-left: 0.2rem">{{ setFilters[i][1] }}</small>
            <span v-if="hoveredIndex === i" class="selected-filters__close"
              ><img src="@/assets/images/close.svg" @click="removeFilter(filter, i + 2)" alt=""
            /></span>
          </div>

          <section v-if="filterSelected" style="position: relative">
            <main class="main__before">
              <small
                ><strong>{{ currentFilter }}</strong></small
              >
              <small style="margin-left: 0.2rem">{{
                currentOperators[currentOperators.length - 1]
              }}</small>
            </main>
            <div>
              <FilterSelection
                @filter-added="applyFilter"
                @operator-selected="addOperator"
                @value-selected="valueSelected"
                @close-selection="closeFilterSelection"
                @filter-accounts="getAccounts"
                :type="filterType"
                :filterName="currentFilter"
                :dropdowns="apiPicklistOptions"
                :apiName="filterApiName"
                :accounts="allAccounts"
                :owners="allUsers"
              />
            </div>
          </section>

          <section style="position: relative">
            <button
              v-if="activeFilters.length < 4 && !selectedWorkflow"
              @click.stop="addingFilter"
              class="add-filter-button"
            >
              <img
                src="@/assets/images/filter.svg"
                class="invert"
                height="12px"
                style="margin-right: 0.25rem"
                alt=""
              />Filter
            </button>
            <div v-outside-click="closeFilters" v-if="filtering">
              <Filters @select-filter="selectFilter" :filterFields="filterFields" />
            </div>
          </section>
        </div>
        <div v-else>
          <div v-if="!updatingOpps" class="bulk-action">
            <div
              v-if="
                !closeDateSelected &&
                !advanceStageSelected &&
                !forecastSelected &&
                !changeFieldsSelected
              "
            >
              <div class="flex-row">
                <!-- <button @click="forecastSelected = !forecastSelected" class="select-btn1">
                  Change Forecast
                  <img
                    src="@/assets/images/monetary.svg"
                    height="14px"
                    style="margin-left: 0.25rem"
                    alt=""
                  />
                </button> -->
                <!-- <button @click="changeFieldsSelected = !changeFieldsSelected" class="select-btn">
                  Bulk Update
                </button> -->
                <!-- <button @click="modifyForecast('add')" class="select-btn2">Start Tracking</button> -->
              </div>
            </div>
            <div class="flex-row-pad" v-if="closeDateSelected">
              <p style="font-size: 14px">How many days ?:</p>
              <input class="number-input" v-model="daysForward" type="number" />
              <button :disabled="!daysForward" class="add-button" @click="pushCloseDate">
                Push Close Date
              </button>
            </div>
            <div class="flex-row-pad" v-if="advanceStageSelected">
              <p style="font-size: 14px">Select Stage:</p>
              <Multiselect
                :options="apiPicklistOptions /*&& apiPicklistOptions['StageName'] ? apiPicklistOptions['StageName'] : []*/"
                @select="setStage($event.value)"
                :v-model="userCRM === 'SALESFORCE' ? dropdownVal['StageName'] : dropdownVal['dealstage']"
                openDirection="below"
                :loading="dropdownLoading"
                style="width: 40.25vw"
                selectLabel="Enter"
                track-by="value"
                label="label"
              >
                <template v-slot:noResult>
                  <p class="multi-slot">No results.</p>
                </template>

                <template v-slot:placeholder>
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Stage
                  </p>
                </template>
              </Multiselect>
              <!-- <p v-else>Add Stage to your update form</p> -->
              <button @click="advanceStage()" class="add-button">Advance Stage</button>
            </div>
            <div class="flex-row-pad" v-if="forecastSelected">
              <p style="font-size: 14px">Select Forecast:</p>
              <Multiselect
                :options="apiPicklistOptions /*&& apiPicklistOptions['ForecastCategoryName'] ? apiPicklistOptions['ForecastCategoryName'] : []*/"
                @select="setForecast($event.value)"
                v-model="dropdownVal['ForecastCategoryName']"
                openDirection="below"
                :loading="dropdownLoading"
                style="width: 40.25vw"
                selectLabel="Enter"
                track-by="value"
                label="label"
              >
                <template v-slot:noResult>
                  <p class="multi-slot">No results.</p>
                </template>

                <template v-slot:placeholder>
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Forecast Category
                  </p>
                </template>
              </Multiselect>

              <button @click="changeForecast(currentCheckList)" class="add-button">
                Change Forecast
              </button>
            </div>
            <div class="flex-row-pad" v-if="changeFieldsSelected">
              <!-- <p style="font-size: 14px">Change Field:</p> -->
              <Multiselect
                :options="filteredSelectOppFields"
                @select="selectedOppVal($event)"
                v-model="selectedOpp"
                openDirection="below"
                :loading="dropdownLoading"
                style="width: 20vw; margin-right: 1rem"
                selectLabel="Enter"
                label="label"
              >
                <template v-slot:noResult>
                  <p class="multi-slot">No results.</p>
                </template>

                <template v-slot:placeholder>
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select field to update
                  </p>
                </template>
              </Multiselect>
              <div v-if="selectedOpp">
                <div
                  v-if="
                    selectedOpp.dataType === 'String' ||
                    selectedOpp.dataType === 'TextArea' ||
                    selectedOpp.dataType === 'Email' ||
                    selectedOpp.dataType === 'Address' ||
                    selectedOpp.dataType === 'Currency' ||
                    selectedOpp.dataType === 'Url'
                  "
                >
                  <input
                    class="sliding input"
                    @input="oppNewValue = $event.target.value"
                    type="text"
                  />
                </div>
                <div v-else-if="selectedOpp.dataType === 'Date'">
                  <input
                    class="sliding"
                    type="date"
                    id="user-input"
                    @input="oppNewValue = $event.target.value"
                  />
                </div>
                <div v-else-if="selectedOpp.dataType === 'DateTime'">
                  <input
                    type="datetime-local"
                    id="start"
                    @input="oppNewValue = $event.target.value"
                    class="sliding"
                  />
                </div>
                <div v-else-if="selectedOpp.dataType === 'Boolean'">
                  <input
                    type="checkbox"
                    id="start"
                    @input="oppNewValue = $event.target.value"
                    class="sliding"
                  />
                </div>
                <div
                  v-else-if="
                    selectedOpp.dataType === 'Phone' ||
                    selectedOpp.dataType === 'Double' ||
                    selectedOpp.dataType === 'Currency' ||
                    selectedOpp.dataType === 'Int' ||
                    selectedOpp.dataType === 'Percent'
                  "
                >
                  <input
                    type="number"
                    @input="oppNewValue = Number($event.target.value)"
                    class="sliding input"
                  />
                </div>
                <div
                  v-if="
                    selectedOpp.dataType === 'Picklist' ||
                    selectedOpp.dataType === 'MultiPicklist' ||
                    (selectedOpp.dataType === 'Reference' && selectedOpp.apiName !== 'AccountId')
                  "
                >
                  <Multiselect
                    :options="
                      selectedOpp.dataType === 'Picklist' ||
                      selectedOpp.dataType === 'MultiPicklist'
                        ? allPicklistOptions[selectedOpp.id]
                        : referenceOpts[selectedOpp.apiName]
                    "
                    @select="oppNewValue = $event.value"
                    @open="
                      selectedOpp.dataType === 'Reference'
                        ? getReferenceOpts(selectedOpp.apiName, selectedOpp.id, field.options)
                        : null
                    "
                    openDirection="below"
                    v-model="dropdownVal[selectedOpp.apiName]"
                    style="width: 20vw"
                    selectLabel="Enter"
                    :loading="loadingProducts"
                    :label="
                      selectedOpp.dataType === 'Picklist' ||
                      selectedOpp.dataType === 'MultiPicklist'
                        ? 'label'
                        : 'name'
                    "
                    :track-by="
                      selectedOpp.dataType === 'Picklist' ||
                      selectedOpp.dataType === 'MultiPicklist'
                        ? 'value'
                        : 'id'
                    "
                    :multiple="selectedOpp.dataType === 'MultiPicklist'"
                    class="sliding"
                  >
                    <template v-slot:noResult>
                      <p class="multi-slot">No results. Try loading more</p>
                    </template>
                    <template v-slot:afterList>
                      <p v-if="showLoadMore" @click="loadMore" class="multi-slot__more">
                        Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                      </p>
                    </template>
                    <template v-slot:placeholder>
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        {{ selectedOpp.referenceDisplayLabel }}
                      </p>
                    </template>
                  </Multiselect>
                </div>
              </div>

              <button @click="bulkUpdate" class="add-button">Update</button>
            </div>
          </div>
          <div class="bulk-action" v-else>
            <SkeletonBox width="400px" height="22px" />
          </div>
        </div>
        <div class="flex-row">
          <div class="tooltip">
            <button @click="manualSync" class="select-btn">
              <img src="@/assets/images/cloud.svg" style="height: 26px" alt="" />
            </button>
            <span class="tooltiptext">Sync Fields</span>
          </div>
          <div v-if="!selectedWorkflow" class="search-bar">
            <img src="@/assets/images/search.svg" style="height: 18px" alt="" />
            <input
              type="search"
              placeholder="search"
              v-model="filterText"
              @input="getFilteredOpps"
            />
          </div>
          <div v-else class="search-bar">
            <img src="@/assets/images/search.svg" style="height: 18px" alt="" />
            <input type="search" placeholder="search" v-model="workflowFilterText" />
          </div>

          <button @click="createOppInstance()" class="add-button">
            {{userCRM === 'SALESFORCE' ? 'Create Opportunity' : 'Create Deal'}}
          </button>
        </div>
      </section>

      <div class="adding-stage-gate2" v-if="stageFormOpen">
        <div class="adding-stage-gate2__header">
          <div>
            <p>
              These fields are required to advance to
              <span
                style="color: #fa646a; background-color: #ffd4d4; border-radius: 4px; padding: 6px"
                >{{ stageGateField }}</span
              >
            </p>
          </div>

          <img
            src="@/assets/images/close.svg"
            style="height: 1rem; margin-top: -0.25rem; margin-right: 0.75rem; cursor: pointer"
            @click="closeStageForm"
            alt=""
          />
        </div>

        <div class="adding-stage-gate2__body">
          <div v-for="(field, i) in stageValidationFields[stageGateField]" :key="i">
            <div
              v-if="
                field.dataType === 'Picklist' ||
                field.dataType === 'MultiPicklist' ||
                (field.dataType === 'Reference' && field.apiName !== 'AccountId')
              "
            >
              <label class="red-label">{{ field.referenceDisplayLabel }} <span>*</span></label>
              <Multiselect
                :options="
                  (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') && allPicklistOptions[field.id]
                    ? allPicklistOptions[field.id]
                    : stageReferenceOpts[field.apiName]
                    ? stageReferenceOpts[field.apiName]
                    : []
                "
                @select="
                  setUpdateValidationValues(
                    /*field.apiName === 'dealstage' ? $event.id :*/
                    field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                    field.apiName === 'dealstage' ? $event.label :
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? $event.value
                      : $event.id,
                  )
                "
                @open="
                  field.dataType === 'Reference'
                    ? getStageReferenceOpts(field.apiName, field.id)
                    : null
                "
                openDirection="below"
                :loading="dropdownLoading"
                v-model="dropdownVal[field.apiName]"
                style="width: 40.25vw; margin-top: 8px"
                selectLabel="Enter"
                :multiple="field.dataType === 'MultiPicklist' ? true : false"
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
                <template v-slot:noResult>
                  <p class="multi-slot">No results.</p>
                </template>
                <template v-slot:placeholder>
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{
                      field.apiName === 'OwnerId'
                        ? currentOwner
                        : `${currentVals[field.apiName]}` !== 'null'
                        ? `${currentVals[field.apiName]}`
                        : `${field.referenceDisplayLabel}`
                    }}
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
                style="width: 40.25vw; margin-top: 8px"
                selectLabel="Enter"
                track-by="integration_id"
                label="name"
                :loading="dropdownLoading || loadingAccounts"
              >
                <template v-slot:noResult>
                  <p class="multi-slot">No results.</p>
                </template>

                <template v-slot:placeholder>
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{ currentAccount }}
                  </p>
                </template>
              </Multiselect>
            </div>
            <div v-else-if="field.dataType === 'String' && field.apiName !== 'NextStep'">
              <label class="red-label">{{ field.referenceDisplayLabel }} <span>*</span></label>
              <input
                id="user-input"
                type="text"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                @input="
                  ;(value = $event.target.value), setUpdateValidationValues(field.apiName, value)
                "
              />
            </div>

            <div
              v-else-if="
                field.dataType === 'TextArea' || (field.length > 250 && field.dataType === 'String')
              "
            >
              <label class="red-label">{{ field.referenceDisplayLabel }} <span>*</span></label>
              <textarea
                id="user-input"
                ccols="30"
                rows="2"
                :placeholder="currentVals[field.apiName]"
                style="width: 40.25vw; border-radius: 6px; padding: 7px"
                v-model="currentVals[field.apiName]"
                @input="
                  ;(value = $event.target.value), setUpdateValidationValues(field.apiName, value)
                "
              >
              </textarea>
            </div>
            <div v-else-if="field.dataType === 'Date'">
              <label class="red-label">{{ field.referenceDisplayLabel }} <span>*</span></label>
              <input
                type="text"
                onfocus="(this.type='date')"
                onblur="(this.type='text')"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                id="user-input"
                @input="
                  ;(value = $event.target.value), setUpdateValidationValues(field.apiName, value)
                "
              />
            </div>
            <div v-else-if="field.dataType === 'DateTime'">
              <label class="red-label">{{ field.referenceDisplayLabel }} <span>*</span></label>
              <input
                type="datetime-local"
                id="start"
                v-model="currentVals[field.apiName]"
                @input="
                  ;(value = $event.target.value), setUpdateValidationValues(field.apiName, value)
                "
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency' ||
                field.dataType === 'Int'
              "
            >
              <label class="red-label">{{ field.referenceDisplayLabel }} <span>*</span></label>
              <input
                id="user-input"
                type="number"
                v-model="currentVals[field.apiName]"
                :placeholder="currentVals[field.apiName]"
                @input="
                  ;(value = $event.target.value), setUpdateValidationValues(field.apiName, value)
                "
              />
            </div>
            <div v-else-if="field.dataType === 'Boolean'">
              <label class="red-label">{{ field.referenceDisplayLabel }}:</label>

              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="booleans"
                @select="setUpdateValidationValues(field.apiName, $event)"
                openDirection="below"
                style="width: 40.25vw; margin-top: 8px"
                selectLabel="Enter"
              >
                <template v-slot:noResult>
                  <p class="multi-slot">No results.</p>
                </template>
                <template v-slot:placeholder>
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{ currentVals[field.apiName] }}
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>

        <div class="adding-stage-gate2__footer">
          <div></div>
          <div v-if="dropdownLoading">
            <PipelineLoader />
          </div>
          <button
            v-else
            @click="updateStageForm()"
            class="add-button"
            style="margin-bottom: 6px; margin-right: -6px"
          >
            Update
          </button>
        </div>
      </div>
      <div style="margin-top: 8px"></div>
      <!-- <div class="results"></div> -->
      <section v-if="!loadingWorkflows" class="table-section">
        <div style="position: relative" v-outside-click="emitCloseEdit" class="table">
          <PipelineHeader
            :oppFields="oppFields"
            @check-all="onCheckAll"
            @sort-opps="sortOpps"
            @set-opps="setOpps"
            @sort-opps-reverse="sortOppsReverse"
            :allSelected="selectedWorkflow ? allWorkflowsSelected : allSelected"
            :extraPipelineFields="extraPipelineFields"
            :fieldOpts="objectFields.list"
          />
          <PipelineTableRow
            :ref="selectedWorkflow ? 'workflowTableChild' : 'pipelineTableChild'"
            :key="i"
            v-for="(opp, i) in selectedWorkflow ? filteredWorkflows : allOpps"
            @create-form="
              createFormInstance(opp, opp.id, opp.integration_id, opp.secondary_data.Pricebook2Id)
            "
            @get-notes="getNotes(opp.id), createFormInstanceForNotes(opp.id, opp.name, opp.integration_id)"
            @checked-box="
              selectedWorkflow ? selectWorkflowCheckbox(opp.id) : selectPrimaryCheckbox(opp.id)
            "
            @inline-edit="inlineUpdate"
            @open-stage-form="openStageForm"
            @current-inline-row="changeCurrentRow"
            @set-dropdown-value="setDropdownValue"
            @get-reference-opts="getReferenceOpts"
            @updated-values="updateOpps"
            @close-inline-editor="closeInlineEditor"
            :dropdownLoading="dropdownLoading"
            :dropdownValue="dropdownValue"
            :closeEdit="closeInline"
            :stages="stagesWithForms"
            :inlineLoader="inlineLoader"
            :picklistOpts="allPicklistOptions"
            :referenceOpts="referenceOpts"
            :opp="opp"
            :index="i"
            :oppFields="oppFields"
            :primaryCheckList="selectedWorkflow ? workflowCheckList : primaryCheckList"
            :updateList="updateList"
            :stageData="newStage"
            :closeDateData="daysForward"
            :ForecastCategoryNameData="newForecast"
            :BulkUpdateName="oppVal ? oppVal.apiName : null"
            :BulkUpdateValue="oppNewValue"
            :currentInlineRow="currentInlineRow"
            :extraPipelineFields="extraPipelineFields"
          />

          <div
            :key="opp.id"
            v-for="(opp, j) in selectedWorkflow ? filteredWorkflows : allOpps"
            :style="`top: ${screenHeight < 900 ? (j + 1) * 10 : (j + 1) * 7}vh;`"
            class="table-row-overlay top-height"
          >
            <div class="cell-name"></div>
            <div
              class="table-cell"
              :key="i"
              v-for="(field, i) in oppFields"
              :class="{
                'table-cell-wide':
                  field.dataType === 'TextArea' ||
                  (field.length > 250 && field.dataType === 'String'),
              }"
            >
              <div
                v-show="currentCell == i && currentInlineRow == j && editingInline"
                class="inline-edit"
              >
                <div class="inline-edit__body">
                  <div
                    v-if="
                      field.dataType === 'TextArea' ||
                      (field.length > 250 && field.dataType === 'String')
                    "
                    class="inline-row"
                  >
                    <textarea
                      id="user-input-wide-inline"
                      :value="
                        field.apiName.includes('__c') || userCRM === 'HUBSPOT'
                          ? opp['secondary_data'][field.apiName]
                          : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                      "
                      @input="setUpdateValues(field.apiName, $event.target.value)"
                    />
                  </div>
                  <div
                    v-else-if="
                      (field.dataType === 'String' && field.apiName !== 'meeting_type') ||
                      (field.dataType === 'String' && field.apiName !== 'meeting_comments') ||
                      (field.dataType === 'String' && field.apiName !== 'NextStep') ||
                      (field.dataType === 'Email' && field.apiName !== 'NextStep')
                    "
                    class="inline-row"
                  >
                    <input
                      @input="setUpdateValues(field.apiName, $event.target.value)"
                      id="user-input-inline"
                      type="text"
                      :value="
                        field.apiName.includes('__c') || userCRM === 'HUBSPOT'
                          ? opp['secondary_data'][field.apiName]
                          : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                      "
                    />
                  </div>

                  <Multiselect
                    v-else-if="(field.apiName === 'StageName' || field.apiName === 'dealstage')"
                    :options="userCRM === 'SALESFORCE' ? allPicklistOptions[field.id] : field.options[0][opp.secondary_data.pipeline].stages"
                    openDirection="below"
                    selectLabel="Enter"
                    style="width: 23vw; font-size: 13px"
                    track-by="value"
                    label="label"
                    @select="
                      setDropdownValue({
                        val: field.apiName === 'StageName' ? $event.value : field.apiName === 'dealstage' ? $event.label : $event.id,
                        oppId: opp.id,
                        oppIntegrationId: opp.integration_id,
                      })
                    "
                    v-model="dropdownVal[field.apiName]"
                  >
                    <template slot="noResult">
                      <p class="multi-slot">No results.</p>
                    </template>

                    <template slot="placeholder">
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        {{ field.apiName === 'StageName' ?
                          opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))] :
                          field.apiName === 'dealstage' ? field.options[0][opp['secondary_data'].pipeline].stages.filter(stage => stage.id === opp['secondary_data'][field.apiName])[0].label :
                          ((
                              field.apiName.includes('__c')
                                ? opp['secondary_data'][field.apiName]
                                : opp['secondary_data'][
                                    capitalizeFirstLetter(camelize(field.apiName))
                                  ]
                            )
                              ? field.apiName.includes('__c')
                                ? opp['secondary_data'][field.apiName]
                                : opp['secondary_data'][
                                    capitalizeFirstLetter(camelize(field.apiName))
                                  ]
                              : field.referenceDisplayLabel)
                        }}
                      </p>
                    </template>
                  </Multiselect>

                  <div
                    v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'"
                  >
                    <Multiselect
                      style="width: 23vw; font-size: 12px"
                      v-if="(field.apiName !== 'StageName' || field.apiName !== 'dealstage')"
                      :options="userCRM === 'SALESFORCE' ? allPicklistOptions[field.id] : field.options"
                      openDirection="below"
                      selectLabel="Enter"
                      :track-by="field.apiName === 'dealstage' ? 'id' : 'value'"
                      label="label"
                      v-model="dropdownVal[field.apiName]"
                      :multiple="field.dataType === 'MultiPicklist' ? true : false"
                      @select="
                        setUpdateValues(
                          field.apiName === 'ForecastCategory'
                            ? 'ForecastCategoryName'
                            : field.apiName,
                            field.apiName === 'dealstage' ? $event.id : $event.value,
                            field.dataType === 'MultiPicklist' ? true : false,
                        )
                      "
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>

                      <template slot="placeholder">
                        <p class="slot-icon">
                          <img src="@/assets/images/search.svg" alt="" />
                          {{
                            (
                              field.apiName.includes('__c') || userCRM === 'HUBSPOT'
                                ? opp['secondary_data'][field.apiName]
                                : opp['secondary_data'][
                                    capitalizeFirstLetter(camelize(field.apiName))
                                  ]
                            )
                              ? field.apiName.includes('__c') || userCRM === 'HUBSPOT'
                                ? opp['secondary_data'][field.apiName]
                                : opp['secondary_data'][
                                    capitalizeFirstLetter(camelize(field.apiName))
                                  ]
                              : field.referenceDisplayLabel
                          }}
                        </p>
                      </template>
                    </Multiselect>
                  </div>
                  <div class="inline-row" v-else-if="field.dataType === 'Date'">
                    <input
                      type="date"
                      id="user-input-inline"
                      :value="
                        field.apiName.includes('__c') || userCRM === 'HUBSPOT'
                          ? opp['secondary_data'][field.apiName]
                          : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                      "
                      @input="setUpdateValues(field.apiName, $event.target.value)"
                    />
                  </div>
                  <div v-else-if="field.dataType === 'DateTime'">
                    <input
                      type="datetime-local"
                      id="user-input-inline"
                      :value="
                        field.apiName.includes('__c') || userCRM === 'HUBSPOT'
                          ? opp['secondary_data'][field.apiName]
                          : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                      "
                      @input="setUpdateValues(field.apiName, $event.target.value)"
                    />
                  </div>
                  <div
                    v-else-if="
                      field.dataType === 'Phone' ||
                      field.dataType === 'Double' ||
                      field.dataType === 'Currency' ||
                      field.dataType === 'Int'
                    "
                    class="inline-row"
                  >
                    <input
                      id="user-input-inline"
                      type="number"
                      :value="
                        field.apiName.includes('__c') || userCRM === 'HUBSPOT'
                          ? opp['secondary_data'][field.apiName]
                          : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                      "
                      @input="setUpdateValues(field.apiName, $event.target.value)"
                    />
                  </div>
                  <div v-else-if="field.dataType === 'Boolean'">
                    <Multiselect
                      v-model="dropdownVal[field.apiName]"
                      :options="booleans"
                      openDirection="below"
                      style="width: 23vw"
                      selectLabel="Enter"
                      @select="setUpdateValues(field.apiName, $event)"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                      <template slot="placeholder">
                        <p class="slot-icon">
                          <img src="@/assets/images/search.svg" alt="" />
                          {{
                            opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                          }}
                        </p>
                      </template>
                    </Multiselect>
                  </div>
                  <div v-else-if="field.dataType === 'Reference'">
                    <Multiselect
                      style="width: 23vw; font-size: 13px"
                      v-model="dropdownVal[field.apiName]"
                      :options="referenceOpts[field.apiName]"
                      @open="getCreateReferenceOpts(field.apiName, field.id, field.options)"
                      :loading="dropdownLoading"
                      openDirection="below"
                      selectLabel="Enter"
                      label="name"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                      <template slot="placeholder">
                        <p class="slot-icon">
                          <img src="@/assets/images/search.svg" alt="" />
                          {{ field.apiName }}
                        </p>
                      </template>
                    </Multiselect>
                  </div>
                </div>
                <div class="inline-edit__footer">
                  <small>ESC to cancel</small>
                  <button
                    @click="inlineUpdate(formData, opp.id, opp.integrationId)"
                    class="add-button"
                  >
                    Update
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-else class="empty-table-section">
        <div v-if="loadingWorkflows">
          <PipelineLoader />
        </div>
        <div v-else>
          <div class="empty-table">
            <div class="table-row">
              <div class="flex-row table-cell-header">
                <h5 style="margin-left: 1rem">
                  No results for the {{ currentWorkflowName }} workflow.
                </h5>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
    <div v-if="loading">
      <Loader loaderText="Pulling in your latest Salesforce data" />
    </div>
  </div>
</template>
<script>
import { SObjects, SObjectField, SObjectPicklist } from '@/services/salesforce'
import { ObjectField, CRMObjects } from '@/services/crm'
import AlertTemplate from '@/services/alerts/'
import CollectionManager from '@/services/collectionManager'
import SlackOAuth from '@/services/slack'
import PipelineTableRow from '@/components/PipelineTableRow'
import PipelineHeader from '@/components/PipelineHeader'
import WorkflowHeader from '@/components/WorkflowHeader'
import WorkflowRow from '@/components/WorkflowRow'
import Modal from '@/components/InviteModal'
import Loader from '@/components/Loader'
import PipelineLoader from '@/components/PipelineLoader'
import Filters from '@/components/Filters'
import FilterSelection from '@/components/FilterSelection'
import User from '@/services/users'

export default {
  name: 'Pipelines',
  components: {
    Modal,
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PipelineTableRow,
    PipelineHeader,
    WorkflowHeader,
    WorkflowRow,
    PipelineLoader,
    Loader,
    Filters,
    FilterSelection,
  },
  data() {
    return {
      screenHeight: window.innerHeight,
      task: false,
      checker: null,
      verboseName: null,
      editingInline: false,
      currentCell: null,
      loadingNext: false,
      viewingProducts: false,
      referenceLoading: false,
      savedOpp: null,
      savedPipeline: null,
      pipelineOptions: [],
      listViews: ['All Opportunites', 'Closing This Month', 'Closing Next Month'],
      dealStages: [],
      stageGateCopy: [],
      stageReferenceOpts: {},
      currentSelectedProduct: null,
      savingProduct: false,
      productName: null,
      editingProduct: false,
      productId: null,
      productIntegrationId: null,
      productRefCopy: {},
      hsPicklistOpts: {},
      apiHSPicklistOpts: {},
      pricebookId: null,
      noteTitle: null,
      noteValue: null,
      addingTemplate: false,
      countSets: 0,
      updateAccountForm: {},
      createData: {},
      savingCreateForm: false,
      productQueryOpts: {},
      objectFields: CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 300 },
        filters: {
          crmObject: this.crmObject,
        },
      }),
      currentProducts: [],
      createProductForm: [],
      addingProduct: false,
      hasNextOriginal: false,
      integrationId: null,
      hasNext: false,
      hasPrev: false,
      currentPage: 1,
      notesLength: 0,
      days: {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
      },
      currentInlineRow: null,
      stageFormOpen: false,
      closeInline: 0,
      inlineLoader: false,
      currentWorkflowName: this.$route.params.title,
      id: this.$route.params.id,
      tableKey: 1200,
      stageGateField: null,
      stageValidationFields: {},
      stagesWithForms: [],
      dropdownVal: {},
      dropdownProductVal: {},
      selectedAccount: null,
      selectedOwner: null,
      currentOwner: null,
      currentAccount: null,
      updatingOpps: false,
      oppId: null,
      primaryCheckList: [],
      workflowCheckList: [],
      allSelected: false,
      allWorkflowsSelected: false,
      updateList: [],
      recapList: [],
      currentVals: [],
      closeDateSelected: false,
      advanceStageSelected: false,
      forecastSelected: false,
      changeFieldsSelected: false,
      selection: false,
      allStages: [],
      allForecasts: [],
      selectedOpp: null,
      selectedresourceName: null,
      oppNewValue: null,
      newStage: null,
      newForecast: null,
      oppVal: null,
      originalList: [],
      daysForward: null,
      loading: false,
      loadingAccounts: false,
      loadingProducts: false,
      accountSobjectId: null,
      dropdownLoading: false,
      loadingWorkflows: false,
      templates: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
      users: CollectionManager.create({ ModelClass: User }),
      currentWorkflow: [],
      selectedWorkflow: false,
      modalOpen: false,
      editOpModalOpen: false,
      addOppModalOpen: false,
      refreshId: null,
      filterText: '',
      workflowFilterText: '',
      storedFilters: [],
      currentList: 'All Opportunities',
      alertInstanceId: null,
      showList: false,
      workList: false,
      showWorkflowList: true,
      showPopularList: true,
      notes: [],
      updateOppForm: [],
      oppFormCopy: [],
      createOppForm: [],
      oppFields: [],
      instanceId: null,
      dropdownValue: {},
      formData: {},
      updateProductData: {},
      noteInfo: '',
      referenceOpts: {},
      createReferenceOpts: {},
      productReferenceOpts: {},
      picklistQueryOpts: {},
      createQueryOpts: {},
      createProductOpts: {},
      picklistQueryOptsContacts: {},
      stagePicklistQueryOpts: {},
      setFilters: {},
      instanceIds: [],
      allAccounts: [],
      allUsers: [],
      filtering: false,
      filterSelected: false,
      activeFilters: [],
      hoveredIndex: null,
      currentFilter: null,
      operatorValue: null,
      currentOperators: [],
      filterType: null,
      filterFields: [],
      filterApiName: null,
      filterValues: [],
      filters: [
        ['NOT_EQUALS', 'StageName', 'Closed Won'],
        ['NOT_EQUALS', 'StageName', 'Closed Lost'],
      ],
      operatorsLength: 0,
      stageGateId: null,
      forecastList: [],
      stageIntegrationId: null,
      stageId: null,
      selectedPriceBook: null,
      pricebookPage: 1,
      savedPricebookEntryId: '',
      showLoadMore: false,
      savedProductedReferenceOps: [],
      booleans: ['true', 'false'],
      ladFilter: {
        apiName: 'LastActivityDate',
        dataType: 'Date',
        referenceDisplayLabel: 'Last Activity Date',
      },
      lmdFilter: {
        apiName: 'LastModifiedDate',
        dataType: 'DateTime',
        referenceDisplayLabel: 'Last Modified Date',
      },
    }
  },
  computed: {
    crmObject(){
      return this.$store.state.user.crm === 'SALESFORCE' ? 'Opportunity' : 'Deal'
    },
    extraPipelineFields() {
      let extras = []
      extras = this.objectFields.list.filter((field) => this.hasExtraFields.includes(field.id))
      return extras
    },
    hasExtraFields() {
      return this.$store.state.user.salesforceAccountRef ? this.$store.state.user.salesforceAccountRef.extraPipelineFields : []
    },
    hasProducts() {
      return this.$store.state.user.organizationRef.hasProducts
    },
    allPicklistOptions() {
      if (this.userCRM === 'HUBSPOT') {
        return this.hsPicklistOpts
      }
      return this.$store.state.allPicklistOptions
    },
    apiPicklistOptions() {
      if (this.userCRM === 'HUBSPOT') {
        return this.apiHSPicklistOpts
      }
      return this.$store.state.apiPicklistOptions
    },
    pricebooks() {
      return this.$store.state.pricebooks ? this.$store.state.pricebooks : []
    },
    noteTemplates() {
      return this.$store.state.templates
    },
    currentCheckList() {
      if (this.primaryCheckList.length > 0) {
        return this.primaryCheckList
      } else if (this.workflowCheckList.length > 0) {
        return this.workflowCheckList
      } else {
        return []
      }
    },
    allOpps() {
      return this.$store.state.allOpps
    },
    user() {
      return this.$store.state.user
    },
    userCRM() {
      return this.$store.state.user.crm
    },
    filteredWorkflows: {
      get: function () {
        return this.currentWorkflow.filter((opp) => opp.name.toLowerCase().includes(this.workflowFilterText.toLowerCase()))
      },
      set: function (newvalue) {
        this.currentWorkflow = newvalue
      },
    },
    filteredSelectOppFields() {
      return this.oppFields
      // return this.oppFields.filter(f => f.label !== 'Stage' && f.label !== 'Close Date' && f.dataType !== 'Reference')
    },
    currentMonth() {
      let date = new Date()
      return date.getMonth()
    },
    currentDay() {
      let date = new Date()
      date = date
        .toLocaleDateString()
        .substring(date.toLocaleDateString().indexOf('/') + 1)
        .substring(0, date.toLocaleDateString().indexOf('/') + 1)
      if (date.includes('/')) {
        date = date.slice(0, -1)

        return '0' + date
      } else {
        return date
      }
    },
    syncDay() {
      if (this.$store.state.user.salesforceAccountRef.lastSyncTime) {
        return this.formatDateTime(this.$store.state.user.salesforceAccountRef.lastSyncTime)
          .substring(
            this.formatDateTime(this.$store.state.user.salesforceAccountRef.lastSyncTime).indexOf(
              '/',
            ) + 1,
          )
          .substring(
            0,
            this.formatDateTime(this.$store.state.user.salesforceAccountRef.lastSyncTime).indexOf(
              '/',
            ),
          )
      } else {
        return null
      }
    },
  },
  async created() {
    if (this.userCRM === 'HUBSPOT') {
      this.filters = [
        ['NOT_EQUALS', 'dealstage', 'closedwon'],
        ['NOT_EQUALS', 'dealstage', 'closedlost'],
        ['NOT_EQUALS', 'dealstage', '3b3df8bd-1824-4c5b-ba5a-2b72fcfae459'],
        ['NOT_EQUALS', 'dealstage', '1266efd0-fbc5-4bea-8379-ac3c83099bfb'],
        ['NOT_EQUALS', 'dealstage', '9968680e-7687-46d1-8130-4d9779a8dc78'],
        ['NOT_EQUALS', 'dealstage', '2698871c-0f35-473c-bf88-76663cfbfca2'],
        ['NOT_EQUALS', 'dealstage', '792b4ff5-9e2d-4013-a621-04226a31a9d0'],
        ['NOT_EQUALS', 'dealstage', '45bd76d3-8eab-401c-b3ab-86782dd7077d'],
        ['NOT_EQUALS', 'dealstage', '4dca2a38-1ffd-4025-9ffd-89b2ccd8d308'],
        ['NOT_EQUALS', 'dealstage', '1aee0da2-e076-423c-ac92-559d324215e3'],
      ]
    }
    this.objectFields.refresh()
    this.$store.dispatch('loadAllOpps', [...this.filters])
    this.getAllForms()
    this.getUsers()
    this.templates.refresh()
  },
  beforeMount() {
    this.selectList()
  },
  mounted() {
    // this.resourceSync()
    if (this.userCRM === 'HUBSPOT') {
      this.getAllHSPicklists()
      this.currentList = 'All Deals'
    }
  },
  watch: {
    primaryCheckList: 'closeAll',
    workflowCheckList: 'closeAll',
    stageGateField: 'stageGateInstance',
    updateOppForm: ['setForms', 'filtersAndOppFields'],
    accountSobjectId: 'getInitialAccounts',
    task: 'checkAndClearInterval',
    dropdownValue: {
      handler(val) {
        let loweredVal = ''
        if (this.userCRM === 'HUBSPOT') {
          loweredVal = val.val.split(' ').join('').toLowerCase()
        }
        if (this.stagesWithForms.includes(val.val) || this.stagesWithForms.includes(loweredVal)) {
          this.openStageForm(val.val, val.oppId, val.oppIntegrationId)
          this.editingInline = false
        } else {
          this.setUpdateValues(this.userCRM === 'SALESFORCE' ? 'StageName' : 'dealstage', val.val)
        }
      },
    },
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    getPipelineOptions(field) {
      const tempPipelineOpts = []
      for (let key in field) {
        tempPipelineOpts.push(field[key])
      }
      this.pipelineOptions = tempPipelineOpts
    },
    closeInlineEditor() {
      this.editingInline = false
    },
    goToWorkflow(id) {
      this.$router.push({ name: 'Pipelines', params: { id: id } })
    },
    toggleViewingProducts() {
      this.viewingProducts == true ? (this.viewingProducts = false) : (this.viewingProducts = true)
      setTimeout(() => {
        this.$refs.allProducts ? this.$refs.allProducts.scrollIntoView({ behavior: 'smooth' }) : ''
      }, 100)
    },
    setUpdateValuesHandler(key, val, oppId, oppIntId, multi) {
      let formData = {}
      if (multi) {
        formData[key] = this.formData[key] ? this.formData[key] + ';' + val : val
      }

      if (val && !multi) {
        formData[key] = val
      }
      setTimeout(() => {
        this.inlineUpdate(formData, oppId, oppIntId)
      }, 500)
    },
    async getAllHSPicklists() {
      this.objectFields.refresh()
      const picklistOpts = {}
      const apiPicklistOpts = {}
      setTimeout(() => {
        for (let i = 0; i < this.objectFields.list.length; i++) {
          const field = this.objectFields.list[i]
          if (field.options.length) {
            picklistOpts[field.id] = field.options
          }
        }
        for (let i = 0; i < this.oppFields.length; i++) {
          const field = this.oppFields[i]
          if (field.options.length) {
            apiPicklistOpts[field.apiName] = field.options
          }
        }
        this.hsPicklistOpts = picklistOpts
        this.apiHSPicklistOpts = apiPicklistOpts
      }, 1000)
    },
    cancelEditProduct() {
      this.dropdownProductVal = {}
      this.editingProduct = !this.editingProduct
    },
    editProduct(integrationId, id, name, secondaryData) {
      this.editingProduct = true
      this.productIntegrationId = integrationId
      this.productId = id
      this.productName = name
      this.currentSelectedProduct = secondaryData
    },
    setTemplate(val, field, title) {
      this.noteTitle = title
      this.addingTemplate = false
      this.noteValue = val
      // let newVal = this.$sanitize(val)
      //   .replace(/<br\s*[\/]?>/gi, '\r\n')
      //   .replace(/<li\s*[\/]?>/gi, '\r\n   -')
      //   .replace(/(<([^>]+)>)/gi, '')
      this.setUpdateValues(field, val)
      this.setUpdateValues('meeting_type', title ? title : null)
    },
    goToNotes() {
      this.$router.push({ name: 'Notes' })
    },
    async loadMore() {
      if (!this.savedPricebookEntryId) {
        return
      }
      try {
        this.loadingProducts = true
        this.savedProductedReferenceOps = [...this.productReferenceOpts['PricebookEntryId']]
        const res = await SObjects.api.getObjects('PricebookEntry', this.pricebookPage, true, [
          ['EQUALS', 'Pricebook2Id', this.savedPricebookEntryId],
        ])
        this.productReferenceOpts['PricebookEntryId'] = [
          ...res.results,
          ...this.savedProductedReferenceOps,
        ]
        if (res.next) {
          this.pricebookPage++
          this.showLoadMore = true
        } else {
          this.showLoadMore = false
        }
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loadingProducts = false
        }, 1000)
      }
    },
    async getPricebookEntries(id) {
      try {
        this.loadingProducts = true
        // change to CRMObjects
        const res = await SObjects.api.getObjects('PricebookEntry', 1, true, [
          ['EQUALS', 'Pricebook2Id', id],
        ])

        this.productReferenceOpts['PricebookEntryId'] = res.results
        this.productList = res.results
        if (res.next) {
          this.pricebookPage++
          this.showLoadMore = true
        } else {
          this.pricebookPage = 1
          this.showLoadMore = false
        }
        this.savedPricebookEntryId = id
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loadingProducts = false
        }, 1000)
      }
    },
    // async getAllPicklist() {
    //   try {
    //     const res = await SObjectPicklist.api.listPicklists({ pageSize: 1000 })
    //     for (let i = 0; i < res.length; i++) {
    //       this.allPicklistOptions[res[i].fieldRef.id] = res[i].values
    //       this.apiPicklistOptions[res[i].fieldRef.apiName] = res[i].values
    //     }
    //   } catch (e) {
    //     console.log(e)
    //   }
    // },
    addProduct() {
      this.addingProduct = !this.addingProduct
      setTimeout(() => {
        this.$refs.product ? this.$refs.product.scrollIntoView({ behavior: 'smooth' }) : null
      }, 100)
    },
    // scrollToFields() {
    //   setTimeout(() => {
    //     this.$refs.product ? this.$refs.product.scrollIntoView() : null
    //   }, 100)
    // },
    getFilteredOpps() {
      if (this.userCRM === 'SALESFORCE') {
        this.$store.dispatch('loadAllOpps', [
          ...this.filters,
          ['CONTAINS', 'Name', this.filterText.toLowerCase()],
        ])
      } else {
        this.$store.dispatch('loadAllOpps', [
          ...this.filters,
          ['CONTAINS', 'dealname', this.filterText.toLowerCase()],
        ])
      }

      if (this.currentList === 'Closing this month') {
        this.stillThisMonth()
      } else if (this.currentList === 'Closing next month') {
        this.stillNextMonth()
      }
    },
    pricebookLabel({ name }) {
      return name
    },

    replaceURLs(message, field) {
      if (!message) return

      var urlRegex = /(((https?:\/\/)|(www\.))[^\s]+)/g
      message.replace(urlRegex, function (url) {
        var hyperlink = url
        if (!hyperlink.match('^https?://')) {
          hyperlink = 'http://' + hyperlink
        }
        return (
          '<a href="' + hyperlink + '" target="_blank" rel="noopener noreferrer">' + url + '</a>'
        )
      })

      this.setUpdateValues(field, message)
    },
    changeCurrentRow(i, cell) {
      this.currentInlineRow = i
      this.currentCell = cell
      this.dropdownVal = {}
      this.editingInline = true
    },
    addToForecastList() {
      let list = []
      for (let i = 0; i < this.currentCheckList.length; i++) {
        list.push(this.allOpps.filter((opp) => opp.id === this.currentCheckList[i])[0])
      }
      this.forecastList = list.map((opp) => opp.integration_id)
    },
    async modifyForecast(action) {
      const oppOrDeal = this.userCRM === 'SALESFORCE' ? 'Opportunities' : 'Deals'
      try {
        await User.api.modifyForecast(action, this.forecastList)
        this.$toast(oppOrDeal + ' added to Tracker.', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error adding ' + oppOrDeal, {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        this.primaryCheckList = []
      }
    },
    async openStageForm(field, id, integrationId) {
      this.setUpdateValues(this.userCRM === 'SALESFORCE' ? 'StageName' : 'dealstage', field)
      this.stageGateField = field
      this.stageFormOpen = true
      this.stageId = id
      this.stageIntegrationId = integrationId
      this.dropdownLoading = true
      try {
        let res
        res = await CRMObjects.api.getCurrentValues({
          resourceType: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
          resourceId: id,
        })
        this.currentVals = res ? res.current_values : {}

        const usersForCurrentOwner = this.allUsers.filter(
          (user) => {
            if (user.salesforce_account_ref) {
              return user.salesforce_account_ref.salesforce_id === this.currentVals['OwnerId']
            } else if (user.hubspot_account_ref) {
              return user.hubspot_account_ref.hubspot_id === this.currentVals['OwnerId']
            }
          }
        )
        usersForCurrentOwner.length
          ? (this.currentOwner = usersForCurrentOwner[0].full_name)
          : (this.currentOwner = 'Owner')

        const firstOpp = this.allOpps.filter((opp) => opp.id === id)[0]
        firstOpp && firstOpp.account_ref
          ? (this.currentAccount = firstOpp.account_ref.name)
          : (this.currentAccount = 'Account')
      } catch (e) {
        console.log(e)
      } finally {
        this.dropdownLoading = false
      }
    },
    closeStageForm() {
      this.stageFormOpen = false
      this.stageGateField = null
      this.resource_id = null
      this.stageId = null
      this.stageIntegrationId = null
    },
    async getReferenceFieldList(key, val, type, eventVal, options, filter) {
      let res = []
      try {
        this.referenceLoading = true
        res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: val,
          value: eventVal ? eventVal : '',
          for_filter: filter ? [filter] : null,
        })
        if (type === 'update') {
          this.referenceOpts[key] = res
        } else if (type === 'createProduct') {
          this.productReferenceOpts[key] = res
        } else if (type === 'stage') {
          this.stageReferenceOpts[key] = res
        } else {
          this.createReferenceOpts[key] = res
        }
      } catch (e) {
        let message = e.response.data.error
          ? e.response.data.error
          : 'Error gathering reference fields'
        this.$toast(message, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        setTimeout(() => {
          this.dropdownLoading = false
          this.referenceLoading = false
        }, 300)
        return res
      }
    },
    emitCloseEdit() {
      this.closeInline += 1
    },
    async inlineUpdate(formData, id, integrationId) {
      this.inlineLoader = true
      this.editingInline = false
      try {
        const res = await CRMObjects.api.updateResource({
          form_data: formData,
          resource_type: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
          form_type: 'UPDATE',
          resource_id: id,
          integration_ids: [integrationId],
          from_workflow: this.selectedWorkflow ? true : false,
          workflow_title: this.selectedWorkflow ? this.currentWorkflowName : 'None',
        })
        if (this.filterText) {
          if (this.userCRM === 'SALESFORCE') {
            this.$store.dispatch('loadAllOpps', [
              ...this.filters,
              ['CONTAINS', 'Name', this.filterText.toLowerCase()],
            ])
          } else {
            this.$store.dispatch('loadAllOpps', [
              ...this.filters,
              ['CONTAINS', 'dealname', this.filterText.toLowerCase()],
            ])
          }
        } else {
          this.$store.dispatch('loadAllOpps', [...this.filters])
        }
        setTimeout(() => {
          if (this.selectedWorkflow) {
            this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
          }
          if (this.storedFilters.length && !this.selectedWorkflow) {
            this.storedFilters[3].reversed
              ? this.sortOppsReverse(
                  this.storedFilters[0],
                  this.storedFilters[1],
                  this.storedFilters[2],
                )
              : this.sortOpps(this.storedFilters[0], this.storedFilters[1], this.storedFilters[2])
          }
          if (this.currentList === 'Closing this month') {
            this.stillThisMonth()
          } else if (this.currentList === 'Closing next month') {
            this.stillNextMonth()
          }
          this.$toast(`${this.userCRM === 'SALESFORCE' ? 'Salesforce' : 'Hubspot'} Update Successful`, {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }, 750)
      } catch (e) {
        this.$toast(`${e.response.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.formData = {}
        setTimeout(() => {
          this.inlineLoader = false
          this.closeInline += 1
        }, 1500)
      }
    },
    setOpps() {
      User.api.getUser(this.user.id).then((response) => {
        this.$store.commit('UPDATE_USER', response)
      })
    },
    closeFilters() {
      this.filtering = false
    },
    closeFilterSelection() {
      this.filterSelected = false
      this.activeFilters = []
      this.operatorValue = null
      this.currentOperator = []
      this.filterValues = []
      this.filters = this.userCRM === 'SALESFORCE' ? [
        ['NOT_EQUALS', 'StageName', 'Closed Won'],
        ['NOT_EQUALS', 'StageName', 'Closed Lost'],
      ] :
      [
        ['NOT_EQUALS', 'dealstage', 'closedwon'],
        ['NOT_EQUALS', 'dealstage', 'closedlost'],
        ['NOT_EQUALS', 'dealstage', '3b3df8bd-1824-4c5b-ba5a-2b72fcfae459'],
        ['NOT_EQUALS', 'dealstage', '1266efd0-fbc5-4bea-8379-ac3c83099bfb'],
        ['NOT_EQUALS', 'dealstage', '9968680e-7687-46d1-8130-4d9779a8dc78'],
        ['NOT_EQUALS', 'dealstage', '2698871c-0f35-473c-bf88-76663cfbfca2'],
        ['NOT_EQUALS', 'dealstage', '792b4ff5-9e2d-4013-a621-04226a31a9d0'],
        ['NOT_EQUALS', 'dealstage', '45bd76d3-8eab-401c-b3ab-86782dd7077d'],
        ['NOT_EQUALS', 'dealstage', '4dca2a38-1ffd-4025-9ffd-89b2ccd8d308'],
        ['NOT_EQUALS', 'dealstage', '1aee0da2-e076-423c-ac92-559d324215e3'],
      ]
    },
    closeListSelect() {
      this.showList = false
    },
    closeWorkSelect() {
      this.workList = false
    },
    async getFilteredObjects(value) {
      this.loadingWorkflows = true
      if (value) {
        this.filters.push([this.operatorValue, this.filterApiName, value])
        this.setFilters[this.activeFilters.length] = [this.operatorValue, value]
      }
      try {
        let res
        if (this.filterText) {
          let textFilters 
          if (this.userCRM === 'SALESFORCE') {
            textFilters = [...this.filters, ['CONTAINS', 'Name', this.filterText.toLowerCase()]]
          } else {
            textFilters = [...this.filters, ['CONTAINS', 'dealname', this.filterText.toLowerCase()]]
          }
          this.$store.dispatch('loadAllOpps', textFilters)
        }
        // else if (this.workflowFilterText) {
        //   const textFilters = [
        //     ...this.filters,
        //     ['CONTAINS', 'Name', this.workflowFilterText.toLowerCase()],
        //   ]
        //   res = await SObjects.api.getObjects('Opportunity', 1, true, textFilters)
        // }
        else {
          this.$store.dispatch('loadAllOpps', [...this.filters])
        }
        if (this.selectedWorkflow) {
          this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
        } else if (this.currentList === 'Closing this month') {
          this.stillThisMonth()
        } else if (this.currentList === 'Closing next month') {
          this.stillNextMonth()
        }
      } catch (e) {
        this.$toast('Error creating filter, please try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loadingWorkflows = false
      }
    },
    addOperator(name) {
      this.operatorValue = name
      switch (name) {
        case 'EQUALS':
          this.currentOperators.length === 0
            ? (this.currentOperators = ['equals'])
            : this.currentOperators.push('equals')
          break
        case 'NOT_EQUALS':
          this.currentOperators.length === 0
            ? (this.currentOperators = ['not equals'])
            : this.currentOperators.push('not equals')
          break
        case 'GREATER_THAN':
          this.currentOperators.length === 0
            ? (this.currentOperators = ['greater than'])
            : this.currentOperators.push('greater than')
          break
        case 'GREATER_THAN_EQUALS':
          this.currentOperators.length === 0
            ? (this.currentOperators = ['greater or equal'])
            : this.currentOperators.push('greater or equal')
          break
        case 'LESS_THAN':
          this.currentOperators.length === 0
            ? (this.currentOperators = ['less than'])
            : this.currentOperators.push('less than')
          break
        case 'LESS_THAN_EQUALS':
          this.currentOperators.length === 0
            ? (this.currentOperators = ['less or equal'])
            : this.currentOperators.push('less or equal')
          break
        case 'CONTAINS':
          this.currentOperators.length === 0
            ? (this.currentOperators = ['contains'])
            : this.currentOperators.push('contains')

          break
        case 'RANGE':
          this.currentOperators.length === 0
            ? (this.currentOperators = ['range'])
            : this.currentOperators.push('range')
          break
        default:
          console.log('(0_o)')
      }
    },
    addingFilter() {
      if (this.filtering === true) {
        this.filtering = false
      } else {
        this.filtering = true
        this.filterSelected = false
      }
    },
    applyFilter(value) {
      this.updateFilterValue = value
      this.operatorsLength += 1
      this.getFilteredObjects(value)
      this.filterSelected = false
      this.activeFilters.push(this.currentFilter)
    },
    valueSelected(value, name) {
      let users = this.allUsers.filter((user) => {
        if (user.salesforce_account_ref) {
          return user.salesforce_account_ref
        } else if (user.hubspot_account_ref) {
          return user.hubspot_account_ref
        }
      })
      let user = null
      if (name === 'OwnerId') {
        user = users.filter((user) => {
          if (user.salesforce_account_ref) {
            return user.salesforce_account_ref.salesforce_id === value
          } else if (user.hubspot_account_ref) {
            return user.hubspot_account_ref.hubspot_id === value
          }
        })
        this.filterValues.push(user[0].full_name)
      } else if (name === 'AccountId') {
        let account = this.allAccounts.filter((account) => account.id === value)
        this.filterValues.push(account[0].name)
      } else {
        this.filterValues.push(value)
      }
    },
    selectFilter(name, type, label) {
      this.filtering = !this.filtering
      this.filterApiName = name
      this.filterType = type
      this.currentFilter = label
      this.filterSelected = true
    },
    removeFilter(name, index) {
      if (this.activeFilters.length > 1) {
        this.activeFilters.splice(index - 2, 1)
      } else {
        this.activeFilters = []
      }

      this.filters.splice(index, 1)
      this.filterValues.splice(index, 1)
      this.currentOperators.splice(index, 1)
      this.getFilteredObjects()
      if (this.activeFilters.length < 3) {
        this.updateOpps()
        this.currentPage = 1
        this.hasNext = this.hasNextOriginal
      }
      this.filterSelected = false
      this.currentFilter = null
      this.operatorValue = null
      this.filterApiName = null
    },
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1)
    },
    camelize(str) {
      return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function (match, index) {
        if (+match === 0) return ''
        return index === 0 ? match.toLowerCase() : match.toUpperCase()
      })
    },
    sortOpps(dT, field, apiName) {
      let newField = this.capitalizeFirstLetter(this.camelize(field))
      if (this.currentWorkflow) {
        if (field === 'Stage' || field === 'dealstage') {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = this.userCRM === 'SALESFORCE' ? a['secondary_data']['StageName'] : a['secondary_data']['dealstage']
            const nameB = this.userCRM === 'SALESFORCE' ? b['secondary_data']['StageName'] : b['secondary_data']['dealstage']
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (field === 'Last Activity') {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}` + 'Date']
            const nameB = b['secondary_data'][`${newField}` + 'Date']
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (dT === 'TextArea' && !apiName.includes('__c')) {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}`]
            const nameB = b['secondary_data'][`${newField}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (apiName.includes('__c') && dT !== 'TextArea') {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${apiName}`]
            const nameB = b['secondary_data'][`${apiName}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (apiName.includes('__c') && dT === 'TextArea') {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${apiName}`]
            const nameB = b['secondary_data'][`${apiName}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}`]
            const nameB = b['secondary_data'][`${newField}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        }
      } else {
        if (field === 'Stage' || field === 'dealstage') {
          this.allOpps.sort(function (a, b) {
            const nameA = this.userCRM === 'SALESFORCE' ? a['secondary_data']['StageName'] : a['secondary_data']['dealstage']
            const nameB = this.userCRM === 'SALESFORCE' ? b['secondary_data']['StageName'] : b['secondary_data']['dealstage']
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (field === 'Last Activity') {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}` + 'Date']
            const nameB = b['secondary_data'][`${newField}` + 'Date']
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (dT === 'TextArea' && !apiName.includes('__c')) {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}`]
            const nameB = b['secondary_data'][`${newField}`]

            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (apiName.includes('__c') && dT !== 'TextArea') {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${apiName}`]
            const nameB = b['secondary_data'][`${apiName}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else if (apiName.includes('__c') && dT === 'TextArea') {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${apiName}`]
            const nameB = b['secondary_data'][`${apiName}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        } else {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}`]
            const nameB = b['secondary_data'][`${newField}`]
            return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
          })
        }
      }

      let custom = false
      this.storedFilters = [dT, field, apiName, { reversed: false }, custom]
    },
    sortOppsReverse(dT, field, apiName) {
      let newField = this.capitalizeFirstLetter(this.camelize(field))

      if (this.currentWorkflow) {
        if (field === 'Stage' || field === 'dealstage') {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = this.userCRM === 'SALESFORCE' ? a['secondary_data']['StageName'] : a['secondary_data']['dealstage']
            const nameB = this.userCRM === 'SALESFORCE' ? b['secondary_data']['StageName'] : b['secondary_data']['dealstage']
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (field === 'Last Activity') {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}` + 'Date']
            const nameB = b['secondary_data'][`${newField}` + 'Date']
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (dT === 'TextArea' && !apiName.includes('__c')) {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}`]
            const nameB = b['secondary_data'][`${newField}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (apiName.includes('__c') && dT !== 'TextArea') {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${apiName}`]
            const nameB = b['secondary_data'][`${apiName}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (apiName.includes('__c') && dT === 'TextArea') {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${apiName}`]
            const nameB = b['secondary_data'][`${apiName}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else {
          this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}`]
            const nameB = b['secondary_data'][`${newField}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        }
      } else {
        if (field === 'Stage' || field === 'dealstage') {
          this.allOpps.sort(function (a, b) {
            const nameA = this.userCRM === 'SALESFORCE' ? a['secondary_data']['StageName'] : a['secondary_data']['dealstage']
            const nameB = this.userCRM === 'SALESFORCE' ? b['secondary_data']['StageName'] : b['secondary_data']['dealstage']
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (field === 'Last Activity') {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}` + 'Date']
            const nameB = b['secondary_data'][`${newField}` + 'Date']
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (dT === 'TextArea' && !apiName.includes('__c')) {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}`]
            const nameB = b['secondary_data'][`${newField}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (apiName.includes('__c') && dT !== 'TextArea') {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${apiName}`]
            const nameB = b['secondary_data'][`${apiName}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else if (apiName.includes('__c') && dT === 'TextArea') {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${apiName}`]
            const nameB = b['secondary_data'][`${apiName}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        } else {
          this.allOpps.sort(function (a, b) {
            const nameA = a['secondary_data'][`${newField}`]
            const nameB = b['secondary_data'][`${newField}`]
            return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
          })
        }
      }

      let custom = false
      this.storedFilters = [dT, field, apiName, { reversed: true }, custom]
    },
    selectPrimaryCheckbox(id, index) {
      if (this.primaryCheckList.includes(id)) {
        this.primaryCheckList = this.primaryCheckList.filter((opp) => opp !== id)
      } else {
        this.primaryCheckList.push(id)
      }
    },
    selectWorkflowCheckbox(id) {
      if (this.workflowCheckList.includes(id)) {
        this.workflowCheckList = this.workflowCheckList.filter((opp) => opp !== id)
      } else {
        this.workflowCheckList.push(id)
      }
    },
    closeAll() {
      if (this.primaryCheckList.length === 0 || this.workflowCheckList.length === 0) {
        this.closeDateSelected = false
        this.advanceStageSelected = false
        this.forecastSelected = false
        this.changeFieldsSelected = false
      }
    },
    setStage(val) {
      this.newStage = val
    },
    setForecast(val) {
      this.newForecast = val
    },
    selectedOppVal(val) {
      this.oppVal = val
    },
    onCheckAll() {
      if (this.selectedWorkflow) {
        if (this.workflowCheckList.length < 1) {
          for (let i = 0; i < this.filteredWorkflows.length; i++) {
            this.workflowCheckList.push(this.filteredWorkflows[i].id)
          }
        } else if (
          this.workflowCheckList.length > 0 &&
          this.workflowCheckList.length < this.filteredWorkflows.length
        ) {
          for (let i = 0; i < this.filteredWorkflows.length; i++) {
            !this.workflowCheckList.includes(this.filteredWorkflows[i].id)
              ? this.workflowCheckList.push(this.filteredWorkflows[i].id)
              : (this.workflowCheckList = this.workflowCheckList)
          }
        } else {
          this.workflowCheckList = []
        }
      } else {
        if (this.primaryCheckList.length < 1) {
          for (let i = 0; i < this.allOpps.length; i++) {
            this.primaryCheckList.push(this.allOpps[i].id)
          }
        } else if (
          this.primaryCheckList.length > 0 &&
          this.primaryCheckList.length < this.allOpps.length
        ) {
          for (let i = 0; i < this.allOpps.length; i++) {
            !this.primaryCheckList.includes(this.allOpps[i].id)
              ? this.primaryCheckList.push(this.allOpps[i].id)
              : (this.primaryCheckList = this.primaryCheckList)
          }
        } else {
          this.primaryCheckList = []
        }
      }
    },
    async updateWorkflow(id) {
      try {
        await AlertTemplate.api.runAlertTemplateNow(id, {
          fromWorkflow: true,
        })
      } catch (e) {
        this.$toast('Error running workflow, refreh page and try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    resetNotes() {
      this.modalOpen = !this.modalOpen
      this.notes = []
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
      this.savedOpp = null
    },
    resetAddOpp() {
      this.addOppModalOpen = !this.addOppModalOpen
      this.savedPipeline = null
    },
    async createFormInstanceForNotes(id, name, integrationId) {
      this.formData = {}
      this.selectedresourceName = name
      this.oppId = id
      this.integrationId = integrationId
      this.noteValue = null
      this.noteTitle = null
      try {
        const res = await CRMObjects.api.getCurrentValues({
          resourceType: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
          resourceId: id,
        })
      } catch (e) {
        console.log(e)
      }
    },
    async createFormInstance(opp, id, integrationId, pricebookId, alertInstanceId = null) {
      pricebookId ? (this.pricebookId = pricebookId) : (this.pricebookId = null)
      this.viewingProducts = false
      this.addingProduct = false
      this.formData = {}
      this.createData = {}
      this.integrationId = integrationId
      this.stageGateField = null
      this.dropdownLoading = true
      this.editOpModalOpen = true
      this.currentVals = []
      this.dropdownVal = {}
      this.currentOwner = null
      this.currentAccount = null
      this.selectedAccount = null
      this.selectedOwner = null
      this.noteValue = null
      this.noteTitle = null
      this.alertInstanceId = alertInstanceId
      this.oppId = id
      this.currentProducts = []
      this.updateProductData = {}
      this.productId = null
      this.productIntegrationId = null
      this.dropdownProductVal = {}
      this.editingProduct = false
      this.savedOpp = opp
      try {
        let res
        res = await CRMObjects.api.getCurrentValues({
          resourceType: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
          resourceId: id,
        })
        this.currentVals = res ? res.current_values : {}
        this.currentProducts = res ? res.current_products : {}

        const usersForCurrentOwner = this.allUsers.filter(
          (user) => {
            if (user.salesforce_account_ref) {
              return user.salesforce_account_ref.salesforce_id === this.currentVals['OwnerId']
            } else if (user.hubspot_account_ref) {
              return user.hubspot_account_ref.hubspot_id === this.currentVals['OwnerId']
            }
          }
        )
        usersForCurrentOwner.length
          ? (this.currentOwner = usersForCurrentOwner[0].full_name)
          : (this.currentOwner = 'Owner')

        const firstOpp = this.allOpps.filter((opp) => opp.id === this.oppId)[0]
        firstOpp && firstOpp.account_ref
          ? (this.currentAccount = firstOpp.account_ref.name)
          : (this.currentAccount = 'Account')

        // if (this.activeFilters.length) {
        //   this.getFilteredObjects()
        // }
      } catch (e) {
        console.log(e)
      } finally {
        pricebookId ? this.getPricebookEntries(pricebookId) : null
        this.dropdownLoading = false
      }
    },
    async createOppInstance() {
      this.formData = {}
      this.dropdownVal = {}
      this.createData = {}
      this.currentVals = []
      this.selectedAccount = null
      this.selectedOwner = null
      this.addOppModalOpen = true
      this.addingProduct = false
      this.stageGateField = null
    },
    async stageGateInstance(field) {
      this.stageGateId = null
      try {
        const res = await CRMObjects.api.createFormInstance({
          resourceType: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
          formType: 'STAGE_GATING',
          stageName: field ? field : this.stageGateField,
        })
        this.stageGateId = res.form_id
      } catch (e) {
        this.$toast('Error creating stage form', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    pushCloseDate() {
      if (this.selectedWorkflow) {
        for (let i = 0; i < this.$refs.workflowTableChild.length; i++) {
          if (this.$refs.workflowTableChild[i].isSelected) {
            this.$refs.workflowTableChild[i].onPushCloseDate()
            this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
          }
        }
        this.workflowCheckList = []
      } else {
        for (let i = 0; i < this.$refs.pipelineTableChild.length; i++) {
          if (this.$refs.pipelineTableChild[i].isSelected) {
            this.$refs.pipelineTableChild[i].onPushCloseDate()
            this.updateOpps()
          }
        }

        this.primaryCheckList = []
      }
    },
    advanceStage() {
      if (this.selectedWorkflow) {
        for (let i = 0; i < this.$refs.workflowTableChild.length; i++) {
          if (this.$refs.workflowTableChild[i].isSelected) {
            this.$refs.workflowTableChild[i].onAdvanceStage()
            this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
          }
        }
        this.workflowCheckList = []
      } else {
        for (let i = 0; i < this.$refs.pipelineTableChild.length; i++) {
          if (this.$refs.pipelineTableChild[i].isSelected) {
            this.$refs.pipelineTableChild[i].onAdvanceStage()
            this.updateOpps()
          }
        }

        this.primaryCheckList = []
      }
    },
    changeForecast() {
      if (this.selectedWorkflow) {
        for (let i = 0; i < this.$refs.workflowTableChild.length; i++) {
          if (this.$refs.workflowTableChild[i].isSelected) {
            this.$refs.workflowTableChild[i].onChangeForecast()
            this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
          }
        }
        this.workflowCheckList = []
      } else {
        for (let i = 0; i < this.$refs.pipelineTableChild.length; i++) {
          if (this.$refs.pipelineTableChild[i].isSelected) {
            this.$refs.pipelineTableChild[i].onChangeForecast()
            this.updateOpps()
          }
        }
        this.primaryCheckList = []
      }
    },
    bulkUpdate() {
      if (!this.selectedOpp || !this.oppVal || !this.oppNewValue) {
        return
      }
      if (this.selectedWorkflow) {
        this.onBulkUpdateWorkflow()
      } else {
        this.onBulkUpdatePrimary()
      }
      this.selectedOpp = null
      this.oppVal = null
      this.oppNewValue = null
    },

    async onBulkUpdatePrimary() {
      for (let i = 0; i < this.$refs.pipelineTableChild.length; i++) {
        if (this.$refs.pipelineTableChild[i].isSelected) {
          this.$refs.pipelineTableChild[i].updatedList.push(this.$refs.pipelineTableChild[i].opp.id)
        }
      }
      try {
        const formData = {}
        formData[this.oppVal.apiName] = this.oppNewValue
        const res = await SObjects.api
          .bulkUpdate({
            form_data: formData,
            resource_type: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
            form_type: 'UPDATE',
            resource_ids: this.primaryCheckList,
          })
          .then((res) => {
            this.verboseName = res.verbose_name
            this.checker = setInterval(() => {
              this.checkTask()
            }, 3000)
          })
      } catch (e) {
        console.log(e)
      }
    },

    async onBulkUpdateWorkflow() {
      for (let i = 0; i < this.$refs.workflowTableChild.length; i++) {
        if (this.$refs.workflowTableChild[i].isSelected) {
          this.$refs.workflowTableChild[i].updatedList.push(this.$refs.workflowTableChild[i].opp.id)
        }
      }
      try {
        const formData = {}
        formData[this.oppVal.apiName] = this.oppNewValue
        const res = await SObjects.api
          .bulkUpdate({
            form_data: formData,
            resource_type: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
            form_type: 'UPDATE',
            resource_ids: this.workflowCheckList,
          })
          .then((res) => {
            this.verboseName = res.verbose_name
            this.checker = setInterval(() => {
              this.checkTask()
            }, 3000)
          })
      } catch (e) {
        console.log(e)
      }
    },

    async checkTask() {
      try {
        this.task = await User.api.checkTasks(this.verboseName)
      } catch (e) {
        console.log(e)
      }
    },

    stopChecker() {
      clearInterval(this.checker)
    },

    checkAndClearInterval() {
      if (this.task.completed == true) {
        this.stopChecker()
        this.workflowCheckList = []
        this.primaryCheckList = []
        if (this.selectedWorkflow) {
          for (let i = 0; i < this.$refs.workflowTableChild.length; i++) {
            if (this.$refs.workflowTableChild[i].isSelected) {
              this.$refs.workflowTableChild[i].updatedList = []
            }
          }
          this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
        } else {
          for (let i = 0; i < this.$refs.pipelineTableChild.length; i++) {
            if (this.$refs.pipelineTableChild[i].isSelected) {
              this.$refs.pipelineTableChild[i].updatedList = []
            }
          }
          this.updateOpps()
        }
        this.$toast('Bulk update complete', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } else {
        return
      }
    },
    setUpdateValues(key, val, multi) {
      if (multi) {
        this.formData[key] = this.formData[key]
          ? this.formData[key] + ';' + val
          : val.split(/&#39;/g)[0]
      }

      if (val && !multi) {
        this.formData[key] = val
      }
      if (key === 'StageName' || key === 'dealstage') {
        this.stagesWithForms.includes(val) || this.stagesWithForms.includes(val ? val.split(' ').join('').toLowerCase() : '')
          ? (this.stageGateField = val)
          : (this.stageGateField = null)
      }
    },
    setUpdateValidationValues(key, val) {
      if (val) {
        this.formData[key] = val
      }
    },
    setCreateValues(key, val) {
      if (val) {
        this.createData[key] = val
      }
    },
    setProductValues(key, val) {
      if (val) {
        this.updateProductData[key] = val
      }
    },
    updateOpps() {
      try {
        if (!this.filterText) {
          this.$store.dispatch('loadAllOpps', [...this.filters])
          if (this.currentList === 'Closing this month') {
            this.stillThisMonth()
          } else if (this.currentList === 'Closing next month') {
            this.stillNextMonth()
          }
        } else {
          this.getFilteredOpps()
        }
        setTimeout(() => {
          if (this.storedFilters.length) {
            this.storedFilters[3].reversed
              ? this.sortOppsReverse(
                  this.storedFilters[0],
                  this.storedFilters[1],
                  this.storedFilters[2],
                )
              : this.sortOpps(this.storedFilters[0], this.storedFilters[1], this.storedFilters[2])
          }
          if (this.activeFilters.length) {
            this.getFilteredObjects()
          }
        }, 2000)
      } catch (e) {
        this.$toast('Error updating Opporunity', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async resourceSync() {
      if (
        this.currentDay !== this.syncDay + '/' &&
        this.currentDay !== this.syncDay &&
        this.currentDay !== '0' + this.syncDay
      ) {
        setTimeout(() => {
          this.loading = true
        }, 300)
        try {
          await CRMObjects.api.resourceSync()
          this.$toast('Daily sync complete', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } catch (e) {
          this.$toast('Error syncing your resources, refresh page', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } finally {
          this.$store.dispatch('refreshCurrentUser')
          this.loading = false
        }
      }
    },
    async manualSync() {
      try {
        await CRMObjects.api.resourceSync()
        this.$toast('Sync complete', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error syncing your resources, refresh page', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        setTimeout(() => {
          this.loading = false
        }, 100)
      }
    },
    async updateStageForm() {
      this.dropdownLoading = true
      try {
        const res = await CRMObjects.api.updateResource({
          form_data: this.formData,
          resource_type: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
          form_type: 'UPDATE',
          resource_id: this.stageId,
          integration_ids: [this.stageIntegrationId],
          stage_name: this.stageGateField ? this.stageGateField : null,
        })
        if (this.filterText) {
          if (this.userCRM === 'SALESFORCE') {
            this.$store.dispatch('loadAllOpps', [
              ...this.filters,
              ['CONTAINS', 'Name', this.filterText.toLowerCase()],
            ])
          } else {
            this.$store.dispatch('loadAllOpps', [
              ...this.filters,
              ['CONTAINS', 'dealname', this.filterText.toLowerCase()],
            ])
          }
        } else {
          this.$store.dispatch('loadAllOpps', [...this.filters])
        }

        setTimeout(() => {
          if (this.storedFilters.length) {
            this.storedFilters[3].reversed
              ? this.sortOppsReverse(
                  this.storedFilters[0],
                  this.storedFilters[1],
                  this.storedFilters[2],
                )
              : this.sortOpps(this.storedFilters[0], this.storedFilters[1], this.storedFilters[2])
          }
          if (this.selectedWorkflow) {
            this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
          }
          if (this.activeFilters.length) {
            this.getFilteredObjects(this.updateFilterValue)
          }
          if (this.currentList === 'Closing this month') {
            this.stillThisMonth()
          } else if (this.currentList === 'Closing next month') {
            this.stillNextMonth()
          }
          this.$toast(`${this.userCRM === 'SALESFORCE' ? 'Salesforce' : 'Hubspot'} Update Successful`, {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }, 750)
      } catch (e) {
        this.$toast(`${e.response.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.closeStageForm()
        this.formData = {}
        this.dropdownLoading = false
      }
    },
    async createProduct(id = this.integrationId) {
      if (this.addingProduct) {
        try {
          const res = await CRMObjects.api.createResource({
            integration_ids: [id],
            form_type: 'CREATE',
            resource_type: 'OpportunityLineItem',
            stage_name: this.stageGateField ? this.stageGateField : null,
            resource_id: this.oppId,
            form_data: this.createData,
          })

          this.$toast('Product created successfully', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } catch (e) {
          this.$toast(`${e.response.data.error}`, {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } finally {
          this.addingProduct = !this.addingProduct
        }
      } else {
        return
      }
    },

    async updateProduct() {
      this.savingProduct = true
      try {
        const res = await CRMObjects.api.updateResource({
          form_data: this.updateProductData,
          from_workflow: this.selectedWorkflow ? true : false,
          workflow_title: this.selectedWorkflow ? this.currentWorkflowName : 'None',
          form_type: 'UPDATE',
          integration_ids: [this.productIntegrationId],
          resource_type: 'OpportunityLineItem',
          resource_id: this.productId,
          stage_name: null,
        })
        const res2 = await CRMObjects.api.getCurrentValues({
          resourceType: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
          resourceId: this.oppId,
        })
        this.currentProducts = res2.current_products
        this.$toast('Product updated successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error updating Product', {
          timeout: 1500,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.editingProduct = false
        this.savingProduct = false
      }
    },
    async updateResource() {
      this.updateList.push(this.oppId)

      this.editOpModalOpen = false
      this.modalOpen = false
      this.addOppModalOpen = false
      try {
        const res = await CRMObjects.api.updateResource({
          // form_id: this.stageGateField ? [this.instanceId, this.stageGateId] : [this.instanceId],
          form_data: this.formData,
          from_workflow: this.selectedWorkflow ? true : false,
          workflow_title: this.selectedWorkflow ? this.currentWorkflowName : 'None',
          form_type: 'UPDATE',
          integration_ids: [this.integrationId],
          resource_type: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
          resource_id: this.oppId,
          stage_name: this.stageGateField ? this.stageGateField : null,
        })
        if (this.filterText) {
          if (this.userCRM === 'SALESFORCE') {
            this.$store.dispatch('loadAllOpps', [
              ...this.filters,
              ['CONTAINS', 'Name', this.filterText.toLowerCase()],
            ])
          } else {
            this.$store.dispatch('loadAllOpps', [
              ...this.filters,
              ['CONTAINS', 'dealname', this.filterText.toLowerCase()],
            ])
          }
        } else {
          this.$store.dispatch('loadAllOpps', [...this.filters])
        }
        setTimeout(() => {
          if (this.storedFilters.length) {
            this.storedFilters[3].reversed
              ? this.sortOppsReverse(
                  this.storedFilters[0],
                  this.storedFilters[1],
                  this.storedFilters[2],
                )
              : this.sortOpps(this.storedFilters[0], this.storedFilters[1], this.storedFilters[2])
          }
          if (this.selectedWorkflow) {
            this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
          }
          if (this.activeFilters.length) {
            this.getFilteredObjects(this.updateFilterValue)
          }
          if (this.currentList === 'Closing this month') {
            this.stillThisMonth()
          } else if (this.currentList === 'Closing next month') {
            this.stillNextMonth()
          }
          this.$toast(`${this.userCRM === 'SALESFORCE' ? 'Salesforce' : 'Hubspot'} Update Successful`, {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.savedOpp = null
          this.savedPipeline = null
        }, 750)
      } catch (e) {
        this.$toast(`${e.response.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.updateList = []
        this.formData = {}
        // this.closeFilterSelection()
      }
    },
    async createResource(product) {
      this.savingCreateForm = true
      try {
        // if (this.userCRM === 'HUBSPOT' && this.formData.dealstage) {
        //   this.formData.dealstage = this.formData.dealstage.split(' ').join('').toLowerCase()
        // }
        let res = await CRMObjects.api.createResource({
          form_data: this.formData,
          form_type: 'CREATE',
          resource_type: this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal',
          stage_name: this.stageGateField ? this.stageGateField : null,
        })
        if (product) {
          this.createProduct(res.integration_id)
        }
        let filter = []
        if (this.filters.length) {
          filter = this.filterText
            ? [...this.filters, ['CONTAINS', 'Name', this.filterText]]
            : this.filters
        }
        const objectType = this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal'
        if (this.userCRM === 'SALESFORCE') {
          this.$store.dispatch('loadAllOpps', [
            ...this.filters,
            ['CONTAINS', 'Name', this.filterText.toLowerCase()],
          ])
        } else {
          this.$store.dispatch('loadAllOpps', [
            ...this.filters,
            ['CONTAINS', 'dealname', this.filterText.toLowerCase()],
          ])
        }
        if (this.storedFilters.length) {
          this.storedFilters[3].reversed
            ? this.sortOppsReverse(
                this.storedFilters[0],
                this.storedFilters[1],
                this.storedFilters[2],
              )
            : this.sortOpps(this.storedFilters[0], this.storedFilters[1], this.storedFilters[2])
        }
        this.$toast(objectType + ' created successfully.', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.savedOpp = null
        this.savedPipeline = null
      } catch (e) {
        console.log(e)
        this.$toast(`${e.response.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.savingCreateForm = false
        this.addOppModalOpen = false
      }
    },
    async selectList(id) {
      if (this.id) {
        this.loadingWorkflows = true
        this.selectedWorkflow = true
        this.refreshId = id ? id : this.id
        try {
          let res = await AlertTemplate.api.runAlertTemplateNow(id ? id : this.id, {
            fromWorkflow: true,
          })
          const results = res.data.results
          const closedList = [
            'Closed Won',
            'Closed Lost',
            'closedwon', 
            'closedlost', 
            '3b3df8bd-1824-4c5b-ba5a-2b72fcfae459',
            '1266efd0-fbc5-4bea-8379-ac3c83099bfb',
            '9968680e-7687-46d1-8130-4d9779a8dc78',
            '2698871c-0f35-473c-bf88-76663cfbfca2',
            '792b4ff5-9e2d-4013-a621-04226a31a9d0',
            '45bd76d3-8eab-401c-b3ab-86782dd7077d',
            '4dca2a38-1ffd-4025-9ffd-89b2ccd8d308',
            '1aee0da2-e076-423c-ac92-559d324215e3',
          ]
          if (this.userCRM === 'SALESFORCE') {
            this.currentWorkflow = results.filter(opp => {
              return !closedList.includes(opp['secondary_data'].StageName)
            })
          } else {
            this.currentWorkflow = results.filter(opp => {
              return !closedList.includes(opp['secondary_data'].dealstage)
            })
          }
          if (this.currentWorkflow.length < 1) {
            this.updateWorkflow(id ? id : this.id)
          }
        } catch (error) {
          this.$toast('Error gathering workflow!', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } finally {
          this.loadingWorkflows = false
          this.hasNext = false
        }
      }
    },
    async updateWorkflowList(title, id) {
      this.refreshId = id
      this.currentWorkflowName = title
      try {
        let res = await AlertTemplate.api.runAlertTemplateNow(id, {
          fromWorkflow: true,
        })
        this.currentWorkflow = res.data.results
        this.filteredWorkflows = this.currentWorkflow
        this.workflowFilterText = this.workflowFilterText + ' '
        this.workflowFilterText = this.workflowFilterText.trim()
      } catch (error) {
        this.$toast('Error updating workflow', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.selectedWorkflow = true
        this.showList = false
        this.workList = false
        if (this.storedFilters.length) {
          this.storedFilters[3].reversed
            ? this.sortWorkflowsReverse(
                this.storedFilters[0],
                this.storedFilters[1],
                this.storedFilters[2],
              )
            : this.sortWorkflows(
                this.storedFilters[0],
                this.storedFilters[1],
                this.storedFilters[2],
              )
        }
      }
    },
    setForms() {
      for (let i = 0; i < this.oppFormCopy.length; i++) {
        if (this.oppFormCopy[i].dataType === 'Reference') {
          this.referenceOpts[this.oppFormCopy[i].apiName] = []
        }
      }
      for (let i = 0; i < this.stageGateCopy.length; i++) {
        if (this.stageGateCopy[i].dataType === 'Reference') {
          this.stageReferenceOpts[this.stageGateCopy[i].apiName] = []
        }
      }

      for (let i = 0; i < this.createOppForm.length; i++) {
        if (this.createOppForm[i].dataType === 'Reference') {
          this.createReferenceOpts[this.createOppForm[i].apiName] = []
        }

        if (this.hasProducts) {
          for (let i = 0; i < this.createProductForm.length; i++) {
            if (this.createProductForm[i].dataType === 'Reference') {
              this.productRefCopy[this.createProductForm[i].apiName] = this.createProductForm[i]
              this.productReferenceOpts[this.createProductForm[i].apiName] = []
            }
          }
        }
      }
    },
    async getReferenceOpts(name, id, options = []) {
      this.dropdownLoading = true
      this.referenceOpts[name] = await this.getReferenceFieldList(name, id, 'update', '', options)
    },
    async getStageReferenceOpts(name, id) {
      this.dropdownLoading = true
      this.stageReferenceOpts[name] = await this.getReferenceFieldList(name, id, 'stage')
    },
    async getCreateReferenceOpts(name, id, options = []) {
      this.dropdownLoading = true
      this.createReferenceOpts[name] = await this.getReferenceFieldList(name, id, 'create', '', options)
    },
    async getProductReferenceOpts(name, id) {
      this.dropdownLoading = true
      this.productReferenceOpts[name] = await this.getReferenceFieldList(name, id, 'createProduct')
    },

    setDropdownValue(val) {
      this.dropdownValue = val
    },
    filtersAndOppFields() {
      this.filterFields = this.updateOppForm[0].fieldsRef.filter(
        (field) =>
          field.apiName !== 'meeting_type' &&
          field.apiName !== 'meeting_comments' &&
          !field.apiName.includes('__c'),
      )
      this.filterFields = [...this.filterFields, this.ladFilter, this.lmdFilter]

      this.updateOppForm[0].fieldsRef.filter((field) => field.apiName === 'AccountId').length
        ? (this.accountSobjectId = this.updateOppForm[0].fieldsRef.filter(
            (field) => field.apiName === 'AccountId',
          )[0].id)
        : this.createOppForm.filter((field) => field.apiName === 'AccountId').length
        ? (this.accountSobjectId = this.createOppForm.filter(
            (field) => field.apiName === 'AccountId',
          )[0].id)
        : (this.accountSobjectId = null)

      this.oppFields = this.updateOppForm[0].fieldsRef.filter(
        (field) =>
          field.apiName !== 'meeting_type' &&
          field.apiName !== 'meeting_comments' &&
          field.apiName !== 'Name' &&
          field.apiName !== 'dealname' &&
          field.apiName !== 'AccountId' &&
          field.apiName !== 'OwnerId' &&
          field.apiName !== 'hubspot_owner_id'
      )
    },
    async getAllForms() {
      this.loading = true
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()

        let stageGateForms
        if (this.userCRM === 'SALESFORCE') {
          this.updateOppForm = res.filter(
            (obj) => obj.formType === 'UPDATE' && obj.resource === 'Opportunity',
          )
          this.createOppForm = res
            .filter((obj) => obj.formType === 'CREATE' && obj.resource === 'Opportunity')[0]
            .fieldsRef.filter(
              (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
            )
          stageGateForms = res.filter(
            (obj) => obj.formType === 'STAGE_GATING' && obj.resource === 'Opportunity',
          )
          this.createProductForm = res.filter(
            (obj) => obj.formType === 'CREATE' && obj.resource === 'OpportunityLineItem',
          )[0].fieldsRef
        } else if (this.userCRM === 'HUBSPOT') {
          this.updateOppForm = res.filter(
            (obj) => obj.formType === 'UPDATE' && obj.resource === 'Deal',
          )
          this.createOppForm = res
            .filter((obj) => obj.formType === 'CREATE' && obj.resource === 'Deal')[0]
            .fieldsRef.filter(
              (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
            )
          stageGateForms = res.filter(
            (obj) => obj.formType === 'STAGE_GATING' && obj.resource === 'Deal',
          )
          // this.createProductForm = res.filter(
          //   (obj) => obj.formType === 'CREATE' && obj.resource === 'OpportunityLineItem',
          // )[0].fieldsRef
        }
        
        if (stageGateForms.length) {
          this.stageGateCopy = stageGateForms[0].fieldsRef
          // this.stageGateCopy = stageGateForms[stageGateForms.length-1].fieldsRef
          let stages = stageGateForms.map((field) => field.stage)
          const newStages = []
          for (let i = 0; i < stages.length; i++) {
            newStages.push(stages[i].split(' ').join('').toLowerCase())
          }
          this.stagesWithForms = newStages
          for (const field of stageGateForms) {
            this.stageValidationFields[field.stage] = field.fieldsRef
          }
        }
        this.oppFormCopy = this.updateOppForm[0].fieldsRef
        this.loading = false
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    async getUsers() {
      try {
        const res = await SObjects.api.getObjectsForWorkflows('User')
        this.allUsers = res.results.filter((user) => user.has_salesforce_integration)
      } catch (e) {
        this.$toast('Error gathering users!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getInitialAccounts() {
      this.loadingAccounts = true

      if (this.accountSobjectId) {
        try {
          const res = await SObjects.api.getSobjectPicklistValues({
            sobject_id: this.accountSobjectId,
          })
          this.allAccounts = res
        } catch (e) {
          console.log(e)
        } finally {
          this.loadingAccounts = false
        }
      }
    },
    async getAccounts(val) {
      this.loadingAccounts = true
      try {
        const res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: this.accountSobjectId,
          value: val,
        })
        this.allAccounts = res
      } catch (e) {
        this.$toast('Error gathering Accounts!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loadingAccounts = false
      }
    },

    // async getObjects() {
    //   this.loading = true
    //   try {
    //     const res = await SObjects.api.getObjectsForWorkflows('Opportunity', true, this.filters)
    //     this.allOpps = res.results
    //     this.originalList = res.results
    //     this.oppTotal = res.count
    //     this.originalOppTotal = res.count
    //   } catch (e) {
    //     this.$toast('Error gathering Opportunities!', {
    //       timeout: 2000,
    //       position: 'top-left',
    //       type: 'error',
    //       toastClassName: 'custom',
    //       bodyClassName: ['custom'],
    //     })
    //   } finally {
    //     this.loading = false
    //   }
    // },

    async getNotes(id) {
      try {
        const res = await CRMObjects.api.getNotes({
          resourceId: id,
        })
        this.modalOpen = true
        if (res.length) {
          this.notes = []
          for (let i = 0; i < res.length; i++) {
            this.notes.push(res[i])
            this.notes = this.notes.filter((note) => note.saved_data__meeting_comments !== null)
            this.notesLength = this.notes.length
          }
        }
      } catch (e) {
        this.$toast('Error gathering Notes!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    closeDatesThisMonth() {
      this.currentPage = 1
      this.selectedWorkflow = false
      const today = new Date(Date.now())
      const todaySplit = today.toLocaleDateString().split('/')
      const todayYear = Number(todaySplit[2])
      const todayMonth = Number(todaySplit[0])
      let nextMonth
      let nextYear
      if (todayMonth === 12) {
        nextMonth = 1
        nextYear = todayYear + 1
      } else {
        nextMonth = todayMonth + 1
      }
      const beginningOfMonth = `${todayYear}-${todayMonth}-01`
      let endOfMonth
      if (nextYear) {
        endOfMonth = `${nextYear}-${nextMonth}-01`
      } else {
        endOfMonth = `${todayYear}-${nextMonth}-01`
      }
      this.$store.dispatch('loadAllOpps', [
        ...this.filters,
        ['GREATER_THAN_EQUALS', 'CloseDate', beginningOfMonth],
        ['LESS_THAN', 'CloseDate', endOfMonth],
      ])
      this.allOpps.length < 20 ? (this.hasNext = false) : (this.hasNext = true)

      this.currentList = 'Closing this month'
      this.showList = false
      this.workList = false
      this.closeFilterSelection()
    },
    stillThisMonth() {
      this.currentPage = 1
      this.allOpps = this.originalList
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth,
      )
      this.allOpps.length < 20 ? (this.hasNext = false) : (this.hasNext = true)

      this.currentList = 'Closing this month'
    },
    closeDatesNextMonth() {
      this.currentPage = 1
      this.selectedWorkflow = false
      const today = new Date(Date.now())
      const todaySplit = today.toLocaleDateString().split('/')
      const nextMonthYear = Number(todaySplit[2])
      const nextMonthMonth = Number(todaySplit[0]) + 1
      let nextNextMonth
      let nextYear
      if (nextMonthMonth >= 12) {
        nextNextMonth = nextMonthMonth - 11
        nextYear = nextMonthYear + 1
      } else {
        nextNextMonth = nextMonthMonth + 1
      }
      const beginningOfMonth = `${nextMonthYear}-${nextMonthMonth}-01`
      let endOfMonth
      if (nextYear) {
        endOfMonth = `${nextYear}-${nextNextMonth}-01`
      } else {
        endOfMonth = `${nextMonthYear}-${nextNextMonth}-01`
      }
      this.$store.dispatch('loadAllOpps', [
        ...this.filters,
        ['GREATER_THAN_EQUALS', 'CloseDate', beginningOfMonth],
        ['LESS_THAN', 'CloseDate', endOfMonth],
      ])
      this.allOpps.length < 20 ? (this.hasNext = false) : (this.hasNext = true)

      this.currentList = 'Closing next month'
      this.showList = false
      this.closeFilterSelection()
    },
    stillNextMonth() {
      this.currentPage = 1
      this.allOpps = this.originalList
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth + 1,
      )
      this.allOpps.length < 20 ? (this.hasNext = false) : (this.hasNext = true)

      this.currentList = 'Closing next month'
    },
    allOpportunities() {
      this.selectedWorkflow = false
      this.$store.dispatch('loadAllOpps')
      this.currentList = this.userCRM === 'SALESFORCE' ? 'All Opportunities' : 'All Deals'
      this.showList = !this.showList
      this.closeFilterSelection()
    },
    weekDay(input) {
      let newer = new Date(input)
      return this.days[newer.getDay()]
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    formatMostRecent(date2) {
      let today = new Date()
      let d = new Date(date2)
      let diff = today.getTime() - d.getTime()
      let days = diff / (1000 * 3600 * 24)
      return Math.floor(days)
    },
  },
  beforeUpdate() {
    if (this.id) {
      this.templates.list.length
        ? (this.currentWorkflowName = this.templates.list.filter(
            (temp) => temp.id === this.id,
          )[0].title)
        : (this.currentWorkflowName = 'Workflow...')
    }
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

@keyframes tooltips-horz {
  to {
    opacity: 0.95;
    transform: translate(0%, 50%);
  }
}

.green {
  color: $dark-green;
  background-color: $white-green;
  padding: 2px 4px;
  border-radius: 4px;
  margin-left: 8px;
}

.inline-edit {
  position: absolute;
  margin-top: 7.5vh;
  background-color: white;
  box-shadow: 1px 1px 20px 1px $very-light-gray;
  padding: 8px 12px;
  border-radius: 8px;
  margin-left: 2px;
  width: 25vw;

  &__body {
    padding: 16px 0px;
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top: 2px solid $soft-gray;
    padding: 8px 0px;
  }
}
.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $light-gray-blue;
  letter-spacing: 0.76px !important;
  margin-top: 20vh;

  .bg-img {
    background-image: url(../assets/images/logo.png);
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
    height: 60px;
    width: 92px;
    opacity: 0.5;
  }
  h4 {
    color: $base-gray;
    margin-bottom: 0;
    margin-top: 8px;
  }
  p {
    font-size: 14px;
  }
}

.input-field {
  border: 1px solid #e8e8e8;
  border-top-left-radius: 6px;
  border-top-right-radius: 6px;
  width: 36vw !important;
  // border-bottom: none !important;
  letter-spacing: 0.8px;
  padding: 8px;
  // color: $base-gray;
}
.input-field,
.input-field::placeholder {
  font: 18px $base-font-family;
}
::placeholder {
  color: $very-light-gray;
}
.current-products {
  font-size: 12px;
  padding-left: 4px;
  width: 40.25vw;

  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  border-radius: 6px;
  padding: 8px;
  margin-top: 16px;

  h4 {
    font-weight: bold;
  }
  span {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: -6px;

    p {
      // background-color: $white-green;
      color: $dark-green;
      padding: 4px;
      border-radius: 4px;
    }

    button {
      border: 1px solid $soft-gray;

      color: $dark-green;
      background-color: white;
      border-radius: 4px;
      padding: 4px 6px;
      font-size: 11px;
      cursor: pointer;
      margin-top: 4px;
      margin-right: 4px;

      img {
        filter: invert(40%);
      }
    }
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    width: 39vw;
    padding: 8px;
    margin-top: 1rem;
    position: sticky;

    p {
      margin-right: 16px;
      cursor: pointer;
      color: $coral;
    }
  }

  // button:hover {
  //   background-color: $base-gray;
  //   opacity: 0.8;
  //   color: white;
  // }
}

.tooltip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2px 0px;
}
.tooltip .tooltiptext {
  visibility: hidden;
  background-color: $base-gray;
  color: white;
  text-align: center;
  border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 4px 0px;
  border-radius: 6px;
  font-size: 11px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1000;
  width: 100px;
  top: 100%;
  left: 50%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}

.input-container {
  position: relative;
  display: inline-block;
  margin: 10px;
}

.basic-slide {
  display: inline-block;
  width: 34vw;
  padding: 9px 0 10px 16px;
  font-family: $base-font-family !important;
  font-weight: 400;
  color: $base-gray;
  background: $white;
  border: 1px solid $soft-gray !important;
  border: 0;
  border-radius: 3px;
  outline: 0;
  text-indent: 70px; // Arbitrary.
  transition: all 0.3s ease-in-out;

  &::-webkit-input-placeholder {
    color: #efefef;
    text-indent: 0;
    font-weight: 300;
  }

  + label {
    display: inline-block;
    position: absolute;
    top: 0;
    left: 0;
    padding: 9px 8px;
    font-size: 15px;
    text-align: center;
    width: 80px;
    // text-shadow: 0 1px 0 rgba(19, 74, 70, 0.4);
    background: $white-green;
    color: $dark-green;
    transition: all 0.3s ease-in-out;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 2px;
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
.basic-slide:focus,
.basic-slide:active {
  color: $base-gray;
  text-indent: 0;
  background: #fff;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;

  &::-webkit-input-placeholder {
    color: #aaa;
  }
  + label {
    transform: translateX(-100%);
  }
}

.form-label {
  color: $dark-green;
  // background-color: $white-green;
  border-radius: 4px;
  padding: 4px;
  margin-bottom: 4px;
  margin-left: -2px;
  width: fit-content;
}

.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;

  ::v-deep div {
    display: none !important;
  }

  label {
    color: $light-gray-blue;
  }
  p {
    color: $light-gray-blue;
  }
}

.light-green-bg {
  background-color: $white-green;
  color: $dark-green !important;
  border: 1px solid $dark-green !important;
}
.note-border {
  border: 1px solid $very-light-gray;
  border-radius: 6px;
  padding: 4px;
  margin: 0px 6px;
  font-size: 12px;
}
.border-bottom {
  border-bottom: 1.25px solid $soft-gray;
}
.sticky {
  position: sticky;
  background-color: white;
  width: 100%;
  left: 0;
  top: 0;
  padding: 0px 6px 8px -2px;
}
.rel {
  position: relative;
}

.adding-stage-gate2 {
  box-shadow: 1px 1px 10px $very-light-gray;
  background-color: white;
  border-radius: 6px;
  margin: 0.5rem 0rem;
  width: 44vw;
  max-height: 70vh;
  left: 32vw;
  top: 17vh;
  position: absolute;
  z-index: 12;
  overflow: scroll;
  &__header {
    border-radius: 6px;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    font-size: 16px;
    letter-spacing: 0.75px;
    padding: 0.75rem 0.5rem 0.75rem 1rem;
    color: $base-gray;
    width: 100%;
    background-color: white;
    img {
      height: 1rem;
      margin-right: 0.5rem;
      filter: invert(5%);
    }
  }
  &__body {
    padding: 16px 8px;
    margin-left: 0.75rem;
    font-size: 13px !important;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    overflow: auto;
  }

  &__footer {
    z-index: 12;
    position: sticky;
    width: 94%;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    bottom: 0;
  }
}
.adding-stage-gate {
  // border: 1px solid $coral;
  border-radius: 0.3rem;
  margin: 0.5rem 0rem;
  padding-top: 16px;
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
    display: flex;
    font-size: 13px;
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    overflow: visible;
    // height: 30vh;
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

.adding-product {
  border-radius: 8px;
  margin: 8px 0px;
  width: 40.25vw;

  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
  }
  &__body {
    padding-top: 4px;
    font-size: 11px !important;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.2rem;
    overflow: auto;

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

  // &__body::-webkit-scrollbar {
  //   width: 2px;
  //   height: 0px;
  // }
  // &__body::-webkit-scrollbar-thumb {
  //   background-color: $dark-green;
  //   box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  //   border-radius: 0.3rem;
  // }
  // &__body::-webkit-scrollbar-track {
  //   box-shadow: inset 2px 2px 4px 0 $soft-gray;
  //   border-radius: 0.3rem;
  // }
  // &__body::-webkit-scrollbar-track-piece {
  //   margin-top: 0.25rem;
  // }
}
.product-text {
  display: flex;
  align-items: center;
  color: $base-gray;
  border-radius: 8px;
  padding: 10px;
  border: 1px solid $soft-gray;
  font-size: 14px;
  letter-spacing: 0.5px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 1px 1px 1px $very-light-gray;
  img {
    // filter: invert(48%) sepia(24%) saturate(1368%) hue-rotate(309deg) brightness(105%) contrast(96%);
    height: 18px;
    margin-left: 4px;
  }
}
.hide {
  display: none;
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
.results {
  margin: 0;
  padding-left: 3px;
  width: 50vw;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  font-size: 18px;
  letter-spacing: 0.5px;
  height: 24px;
}
.pagination {
  width: 100vw;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  margin: 8px 0px 0px 0px;

  h6 {
    span {
      letter-spacing: 0.5px;
      color: $gray;
    }
  }
  &-num {
    margin-right: 8px;
    font-size: 11px;
    border-radius: 6px;
    border: none;
    background-color: $dark-green;
    color: white;
    padding: 6px 8px;
  }
  &-num2 {
    margin-right: 8px;
    font-size: 11px;
    border-radius: 6px;
    border: none;
    background-color: $very-light-gray;
    color: $white;
    padding: 3px 6px;
  }
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.height-s {
  height: 36px;
  margin-top: 8px;
}
.between {
  justify-content: space-between;
  width: 100%;
}
select {
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  background-color: #fafafa;
  height: 40px;
  width: 100%;
  background-image: url('../assets/images/dropdown.svg');
  background-size: 1rem;
  background-position: 100%;
  background-repeat: no-repeat;
  border: 1px solid #ccc;
  padding-left: 0.75rem;
  border-radius: 0;
}
.cancel {
  border: 1px solid $soft-gray;
  font-weight: 400 !important;
  letter-spacing: 1px;
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  margin-right: 0.5rem;
  color: $coral !important;
}
.select-btn1 {
  // box-shadow: 1px 1px 1px $very-light-gray;
  border: 1px solid $soft-gray;
  letter-spacing: 1px;
  padding: 8px 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background-color: white;
  cursor: pointer;
  margin-right: 0.5rem;
  color: $base-gray;
  span {
    padding: 2px 6px;
    background-color: $off-white;
    color: $dark-green;
    border-radius: 6px;
    margin-left: 8px;
  }
  // img {
  //   filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  // }
}
.select-btn {
  // box-shadow: 1px 1px 1px $very-light-gray;
  letter-spacing: 1px;
  border: 1px solid $soft-gray;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9px;
  background-color: white;
  cursor: pointer;
  // color: $dark-green;
  margin-right: 0.5rem;
  transition: all 0.25s;

  img {
    height: 18px !important;
  }
}
.pipeline-header {
  font-size: 11px;
  color: $light-gray-blue;
  margin-left: 4px;
}
.select-btn2 {
  border: 0.5px solid $very-light-gray;
  padding: 0.375rem 0.75rem;
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
    height: 1.05rem !important;
  }
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
input[type='date']::-webkit-datetime-edit-text,
input[type='date']::-webkit-datetime-edit-month-field,
input[type='date']::-webkit-datetime-edit-day-field,
input[type='date']::-webkit-datetime-edit-year-field {
  color: #888;
  cursor: pointer;
  padding-left: 0.5rem;
}
input {
  padding: 7px;
}
h3 {
  font-size: 22px;
}
.table-section {
  margin: 0;
  padding: 0;
  min-height: 50vh;
  max-height: 88vh;
  overflow: scroll;
  border-radius: 12px;
  border: 1px solid #e8e8e8;
  border-collapse: separate;
  border-spacing: 3px;
  background-color: white;
}
// .table-section::-webkit-scrollbar {
//   width: 0px;
//   height: 8px;
// }
// .table-section::-webkit-scrollbar-thumb {
//   background-color: $dark-green;
//   box-shadow: inset 4px 4px 6px 0 rgba(rgb(243, 240, 240), 0.5);
//   border-radius: 0.3rem;
// }
// .table-section::-webkit-scrollbar-track {
//   box-shadow: inset 4px 4px 8px 0 $soft-gray;
//   border-radius: 0.3rem;
// }
// .table-section::-webkit-scrollbar-track-piece:end {
//   margin-right: 50vw;
// }
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
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
    font-size: 12px;
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
.empty-table-section {
  height: 30vh;
  margin-top: 2rem;
  border-radius: 5px;
  border: 1px solid #e8e8e8;
  // box-shadow: 1px 1px 20px 1px $soft-gray;
  background-color: $off-white;
}
.table {
  display: table;
  overflow: scroll;
  width: 100vw;
}
.empty-table {
  display: table;
  width: 98vw;
}
.table-row {
  display: table-row;
  left: 0;
}
.top-height {
}
.table-row-overlay {
  top: 10vh;
  z-index: 20;
  position: absolute;
  display: table-row;

  // height: 100%;
}
.table-cell {
  display: table-cell;
  min-width: 16vw;
  border: none;
  font-size: 13px;
}
.table-cell-wide {
  display: table-cell;
  min-width: 26vw;
  border: none;
  font-size: 13px;
}
.cell-name {
  min-width: 21.5vw;
  display: table-cell;
  padding-left: 4px;
}
.modal-container {
  background-color: $white;
  overflow-y: scroll;
  overflow-x: hidden;
  width: 80vw;
  // min-height: 50vh;
  height: 80vh;
  align-items: center;
  border-radius: 0.5rem;
  padding: 0px 4px;

  &__footer {
    position: absolute;
    display: flex;
    flex-direction: row;
    align-items: center;
    bottom: 0;
    right: 16px;
    padding: 0px 8px;
    background-color: white;

    p {
      font-size: 12px;
      color: $light-gray-blue;
    }

    button {
      margin-right: 0px;
      margin-left: 60vw;
      margin-bottom: 12px;
    }
  }
}
.opp-modal-container {
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  background-color: white;
  width: 44vw;
  height: 90vh;
  border-radius: 0.5rem;
  padding: 1rem;
  // border: 1px solid #e8e8e8;
}
.opp-modal {
  width: 42vw;
  height: 80vh;
  display: flex;
  flex-direction: column;
  // flex-wrap: wrap;
  gap: 0.25rem;
  padding: 8px;
  overflow-y: scroll;
  overflow-x: hidden;
  max-height: 70vh;
  margin-bottom: 8px;
  color: $base-gray;
  font-size: 16px;
  letter-spacing: 0.75px;
  div {
    // margin-right: -1.25rem;
  }
}
.note-container {
  height: 60vh;
  overflow-y: scroll;
  width: 80vw;
  padding: 0px 16px 8px 8px;
  margin: 0;
}
.note-container::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.note-container::-webkit-scrollbar-thumb {
  background-color: $very-light-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 0.3rem;
}
.note-container::-webkit-scrollbar-track {
  box-shadow: inset 2px 2px 4px 0 $soft-gray;
  border-radius: 0.3rem;
}
.note-container::-webkit-scrollbar-track-piece {
  margin-top: 0.25rem;
}
.note-section {
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  margin-top: -8px;
  letter-spacing: 0.75px !important;
  font-family: $base-font-family;
  &__title {
    font-size: 19px;
    color: $base-gray;
    padding: 0;
  }
  &__body {
    color: $base-gray;
    font-family: $base-font-family;
    word-wrap: break-word;
    white-space: pre-wrap;
    font-size: 14px;
  }
  &__date {
    color: $mid-gray;
    font-size: 12px;
    margin-top: -14px;
    margin-bottom: 8px;
    letter-spacing: 0.6px;
  }
}

[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
input[type='search'] {
  // width: 60px;
  border: none;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
  width: 150px;
}
input[type='text']:focus {
  outline: none;
  cursor: text;
}
input[type='checkbox'] {
  cursor: pointer;
}
div[id^='user-input'] {
  // display: none;
  outline: 1px solid yellow !important;
}
select {
  cursor: pointer;
}
option:not(:first-of-type) {
  color: black;
}
header,
section {
  margin: 0;
  padding: 0px;
}
.divArea:focus {
  outline: none;
}
.divArea {
  -moz-appearance: textfield-multiline;
  -webkit-appearance: textarea;
  resize: both;
  height: 50vh;
  width: 36vw;
  min-height: 20vh;
  // margin-top: -20px;
  border-bottom-left-radius: 6px;
  border-bottom-right-radius: 6px;
  border: 1px solid #e8e8e8;
  border-top: none;
  overflow-y: scroll;
  font-family: inherit;
  font-style: inherit;
  font-size: 13px;
  padding: 12px;
}
.div-placeholder {
  position: absolute;
  top: -12px;
  left: 10px;
  z-index: -1;
  color: $very-light-gray;
  opacity: 0.8;
}
// .divArea:hover {
//   border: 1px solid #e8e8e8;
//   border-radius: 4px;
// }
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  letter-spacing: 1px;
  h4 {
    font-size: 20px;
  }
}
.flex-row-pad {
  margin-top: -1rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0rem 0.5rem;
  justify-content: flex-start;
  position: relative;
  z-index: 15;
  p {
    margin-right: 0.5rem;
  }
  button {
    margin-left: 0.5rem;
  }
}
.bulk-action {
  margin: 0rem;
  &__title {
    font-weight: bold;
    font-size: 14px;
    color: $base-gray;
    margin-left: 0.5rem;
  }
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.flex-row-spread-start {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
}
.pipelines {
  padding: 28px 0px 0px 72px;
  color: $base-gray;
  margin: 0 1rem 0 0.5rem;
  letter-spacing: 0.75px !important;
}
.pipelines:focus {
  outline: none;
}
.invert {
  filter: invert(80%);
}
.fullInvert {
  filter: invert(99%);
}
.add-button:disabled {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background-color: $gray;
  cursor: text;
  color: white;
  letter-spacing: 0.75px;
}
.add-button:disabled:hover {
  transform: none;
}
.add-filter-button {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background-color: transparent;
  cursor: pointer;
  color: $base-gray;
  letter-spacing: 0.75px !important;

  img {
    filter: invert(70%);
  }
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
.add-button__ {
  display: flex;
  align-items: center;
  border: none;
  padding: 8px 12px;
  font-size: 14px;
  border-radius: 6px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  letter-spacing: 0.75px;
  span {
    padding: 2px 6px;
    background-color: $off-white;
    color: $dark-green;
    border-radius: 4px;
    margin-left: 8px;
  }
}
.add-button:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.add-button__:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.search-bar {
  background-color: white;
  // box-shadow: 1px 1px 1px $very-light-gray;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border-radius: 8px;
  margin-right: 0.5rem;
}
#user-input-inline {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background-color: white;
  width: 23vw;
  font-family: $base-font-family;
  letter-spacing: 0.75px;
  padding: 8px 12px;
}
#user-input-wide-inline {
  border: 1px solid #e8e8e8;
  height: 140px;
  border-radius: 8px;
  background-color: white;
  min-height: 2.5rem;
  width: 23vw;
  font-family: $base-font-family;
  letter-spacing: 0.75px;
  padding: 8px 12px;
}
#user-input-wide-inline {
  outline: none;
}
#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background-color: white;
  min-height: 2.5rem;
  width: 40.25vw;
  font-family: $base-font-family;
  letter-spacing: 0.75px;
  padding: 8px 12px;
  margin-top: 8px;
}
#user-input > div {
  color: red !important;
}
#user-input:focus,
#user-input-inline:focus {
  outline: none;
}
.number-input {
  background-color: $off-white;
  box-shadow: 1px 1px 1px $gray;
  border: 2px solid $light-orange-gray;
  border-radius: 5px;
  min-height: 4vh;
  margin-right: 1rem;
  margin-left: 0.5rem;
  width: 6vw;
}
#update-input:focus,
.number-input:focus {
  outline: 1px solid $dark-green;
}
.header {
  font-size: 18px;
  padding: 0;
  letter-spacing: 0.5px;
  margin-bottom: 0.2rem;
}
.selected-filters {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  max-width: 50vw;
  margin-top: 1rem;
  overflow: scroll;
  padding: 0;

  &__close {
    background-color: $white-green;
    backdrop-filter: blur(0.5px);
    opacity: 4;
    border: none;
    margin-left: -1rem;
    padding: 0rem 0.1rem 0rem 0.1rem;
    min-height: 3vh;

    img {
      height: 0.9rem;
      filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
    }
  }
}
.main {
  border: none;
  height: 5vh;
  max-width: 10vw;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background-color: $white-green;
  cursor: pointer;
  color: $dark-green;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
}
.main:hover {
  overflow: visible;
  white-space: normal;
  max-width: none;
}

main > span {
  display: none;
}
main:hover > span {
  display: block;
}
.main__before {
  display: flex;
  align-items: center;
  flex-direction: row;
  border: none;
  min-height: 5vh;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  font-weight: bold;
}
.text-button {
  border: none;
  font-size: 13px;
  background-color: transparent;
  margin-right: 8px;
  color: $base-gray;
  letter-spacing: 0.75px;
}
.list-section {
  z-index: 4;
  position: absolute;
  top: 10vh;
  left: 88px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 20vw;
  max-height: 70vh;
  overflow: scroll;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  letter-spacing: 0.75px;
  &__title {
    position: sticky;
    top: 0;
    z-index: 5;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.75px;
    padding-left: 0.75rem;
    font-size: 16px;
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
    cursor: pointer;
    img {
      margin-top: 2px;
    }
  }
  &__sub-title {
    font-size: 12px;
    letter-spacing: 0.3px;
    display: flex;
    align-items: center;
    margin-left: 0.75rem;
    margin-top: 1rem;
    color: $base-gray;
    cursor: pointer;
    width: 100%;
    img {
      margin: 2px 0px 0px 3px;
      height: 0.75rem;
      filter: invert(70%);
    }
  }
}
.list-button {
  display: flex;
  align-items: center;
  height: 4.5vh;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75rem;
  border-radius: 6px;
  color: $base-gray;
  cursor: pointer;
  font-size: 12px;
  letter-spacing: 0.75px;
}
.list-button:hover {
  color: $dark-green;
  background-color: $off-white;
}
.filter {
  color: #41b883;
  margin-left: 0.2rem;
}
.cancel {
  color: $dark-green;
  font-weight: bold;
  margin-left: 1rem;
  cursor: pointer;
}
.flex-end-opp {
  width: 100%;
  padding: 4px 12px 4px 0px;
  height: 4rem;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}
textarea {
  resize: vertical;
}

a {
  text-decoration: none;
}
.logo {
  border-radius: 4px;
  margin-right: 8px;
  margin-top: 4px;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
.results-2 {
  font-size: 11px;
  margin-right: 16px;
  color: $gray;
}
.note-templates {
  display: flex;
  justify-content: flex-end;
  font-size: 12px;
  padding: 12px 6px;
  margin-top: -18px;
  border: none;
  // border-bottom-left-radius: 4px;
  // border-bottom-right-radius: 4px;
  cursor: pointer;
  width: 37vw;

  &__content {
    display: flex;
    flex-direction: row;
    align-items: center;
  }
  img {
    filter: invert(50%);
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
  margin-top: -18px;
  border: none;
  // border-bottom-left-radius: 4px;
  // border-bottom-right-radius: 4px;
  width: 37vw;
  height: 80px;
  overflow: scroll;

  &__content {
    border-radius: 4px;
    border: none;
    color: $base-gray;
    padding: 8px 6px;
    margin-bottom: 8px;
    cursor: pointer;
  }
  &__content:hover {
    opacity: 0.6;
  }
}
.close-template {
  position: absolute;
  bottom: 50px;
  left: 35.5vw;
  z-index: 3;
  cursor: pointer;
  background-color: black;
  border-radius: 3px;
  opacity: 0.6;
  img {
    filter: invert(99%);
  }
}
.label {
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
.red-label {
  // background-color: $light-red;
  color: $coral;
  padding: 6px 4px;
  border-radius: 4px;
  margin-bottom: 4px !important;
}

.sliding {
  animation: slideOnOpen 1s;
  animation-fill-mode: forwards;
}

@keyframes slideOnOpen {
  from {
    width: 0;
  }
  to {
    width: 15rem;
  }
}
.input {
  min-height: 40px;
  // display: block;
  // padding: 8px 40px 0 8px;
  border-radius: 5px;
  border: 1px solid #e8e8e8;
  background: #fff;
  font-size: 14px;
}
// .results-2 {
//   font-size: 11px;
//   margin-right: 16px;
//   color: $gray;
// }
// .note-templates {
//   display: flex;
//   justify-content: flex-end;
//   font-size: 12px;
//   padding: 12px 6px;
//   margin-top: -34px;
//   border: 1px solid $soft-gray;
//   border-bottom-left-radius: 4px;
//   border-bottom-right-radius: 4px;
//   cursor: pointer;
//   width: 40.25vw;

//   &__content {
//     display: flex;
//     flex-direction: row;
//     align-items: center;
//   }
//   img {
//     filter: invert(50%);
//     height: 12px;
//   }
//   &__content:hover {
//     opacity: 0.6;
//   }
// }

// .note-templates2 {
//   display: flex;
//   flex-direction: row;
//   align-items: center;
//   justify-content: flex-start;
//   flex-wrap: wrap;
//   gap: 24px;
//   font-size: 12px;
//   padding: 12px 6px;
//   margin-top: -34px;
//   border: 1px solid $soft-gray;
//   border-bottom-left-radius: 4px;
//   border-bottom-right-radius: 4px;
//   width: 40.25vw;
//   height: 80px;
//   overflow: scroll;

//   &__content {
//     border-radius: 4px;
//     border: 0.5px solid $base-gray;
//     color: $base-gray;
//     padding: 8px 6px;
//     margin-bottom: 8px;
//     cursor: pointer;
//   }
//   &__content:hover {
//     opacity: 0.6;
//   }
// }
// .close-template {
//   position: absolute;
//   bottom: 56px;
//   right: 20px;
//   z-index: 3;
//   cursor: pointer;
//   background-color: black;
//   border-radius: 3px;
//   opacity: 0.6;
//   img {
//     filter: invert(99%);
//   }
// }
// .label {
//   display: inline-block;
//   padding: 6px;
//   font-size: 14px;
//   text-align: center;
//   min-width: 80px;
//   margin-top: 12px;
//   background-color: $white-green;
//   color: $dark-green;
//   font-weight: bold;
//   border-top-left-radius: 4px;
//   border-top-right-radius: 4px;
// }
// .red-label {
//   background-color: #fa646a;
//   color: white;
//   display: inline-block;
//   padding: 6px;
//   font-size: 14px;
//   text-align: center;
//   min-width: 80px;
//   margin-top: 12px;
//   margin-left: 2px;
//   font-weight: bold;
//   border-top-left-radius: 4px;
//   border-top-right-radius: 4px;
// }
</style>