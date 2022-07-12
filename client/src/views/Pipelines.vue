<template>
  <div class="pipelines">
    <Modal
      v-if="modalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetNotes()
        }
      "
    >
      <div v-if="notes.length" class="modal-container rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h4>Notes</h4>
          </div>

          <div class="flex-row">
            <small class="note-border">Total: {{ notesLength }}</small>
            <small class="note-border light-green-bg"
              >Most recent: {{ formatMostRecent(notes[0].submission_date) }} days</small
            >
            <small class="note-border"
              >Oldest: {{ formatMostRecent(notes[notes.length - 1].submission_date) }} days</small
            >
          </div>

          <!-- <img
            src="@/assets/images/close.svg"
            style="height: 1.5rem; margin-top: -0.5rem; margin-right: 0.5rem; cursor: pointer"
            @click="resetNotes"
            alt=""
          /> -->
        </div>
        <section class="note-section" :key="i" v-for="(note, i) in notes">
          <p class="note-section__title">
            {{ note.saved_data__meeting_type ? note.saved_data__meeting_type : 'Untitled' }}
          </p>
          <p class="note-section__date">
            {{ weekDay(note.submission_date) }} {{ formatDateTime(note.submission_date) }}
          </p>
          <pre class="note-section__body">{{ note.saved_data__meeting_comments }}</pre>
        </section>
      </div>
      <div v-else class="modal-container">
        <div class="flex-row-spread">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h4>Notes</h4>
          </div>

          <div class="flex-row">
            <small class="note-border">Total: 0</small>
            <small class="note-border light-green-bg">Most recent: 0 days</small>
            <small class="note-border">Oldest: 0 days</small>
          </div>
        </div>
        <section class="note-section">
          <p class="note-section__body">No notes for this opportunity</p>
        </section>
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
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3>Create Opportunity</h3>
          </div>
          <img
            src="@/assets/images/close.svg"
            style="height: 1.25rem; margin-top: -1rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetAddOpp"
            alt=""
          />
        </div>
        <div class="opp-modal">
          <section :key="field.id" v-for="field in createOppForm">
            <div
              v-if="
                field.dataType === 'TextArea' ||
                (field.dataType === 'String' && field.apiName === 'NextStep')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <textarea
                id="user-input"
                ccols="30"
                rows="4"
                style="width: 36.5vw; border-radius: 0.4rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div v-else-if="field.dataType === 'String'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="user-input"
                type="text"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.apiName === 'AccountId'">
              <p>{{ field.referenceDisplayLabel }}</p>
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
                style="width: 18vw"
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
                    Select Account
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
              <p>{{ field.referenceDisplayLabel }}:</p>

              <Multiselect
                v-model="currentVals[field.apiName]"
                :options="
                  field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                    ? createQueryOpts[field.apiName]
                    : createReferenceOpts[field.apiName]
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
                    ? getReferenceFieldList(field.apiName, field.id, 'create1', $event)
                    : null
                "
                :multiple="field.dataType === 'MultiPicklist' ? true : false"
                openDirection="below"
                style="width: 18vw"
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
                    {{ `${field.referenceDisplayLabel}` }}
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
                <div class="adding-stage-gate__header">
                  <img src="@/assets/images/warning.svg" alt="" />
                  <p>This Stage has validation rules</p>
                </div>
                <div class="adding-stage-gate__body">
                  <div v-for="(field, i) in stageValidationFields[stageGateField]" :key="i">
                    <div
                      v-if="
                        field.dataType === 'Picklist' ||
                        field.dataType === 'MultiPicklist' ||
                        (field.dataType === 'Reference' && field.apiName !== 'AccountId')
                      "
                    >
                      <p>{{ field.referenceDisplayLabel }}:</p>
                      <Multiselect
                        :options="
                          field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                            ? stagePicklistQueryOpts[field.apiName]
                            : createReferenceOpts[field.apiName]
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
                        openDirection="below"
                        v-model="dropdownVal[field.apiName]"
                        style="width: 18vw"
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
                          <p class="multi-slot">No results.</p>
                        </template>
                        <template slot="placeholder">
                          <p class="slot-icon">
                            <img src="@/assets/images/search.svg" alt="" />
                            {{ `${field.apiName}'s` }}
                          </p>
                        </template>
                      </Multiselect>
                    </div>
                    <div v-else-if="field.apiName === 'AccountId'">
                      <p>{{ field.referenceDisplayLabel }}*</p>
                      <Multiselect
                        v-model="selectedAccount"
                        :options="allAccounts"
                        @search-change="getAccounts($event)"
                        @select="setUpdateValidationValues(field.apiName, $event.id)"
                        openDirection="below"
                        style="width: 18vw"
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
                            Accounts
                          </p>
                        </template>
                      </Multiselect>
                    </div>
                    <div v-else-if="field.dataType === 'String' && field.apiName !== 'NextStep'">
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
                      <textarea
                        id="user-input"
                        ccols="30"
                        rows="2"
                        :placeholder="currentVals[field.apiName]"
                        style="width: 20vw; border-radius: 6px; padding: 7px"
                        v-model="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      >
                      </textarea>
                    </div>
                    <div v-else-if="field.dataType === 'Date'">
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
                        field.dataType === 'Currency'
                      "
                    >
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
                      <p>{{ field.referenceDisplayLabel }}:</p>

                      <Multiselect
                        v-model="dropdownVal[field.apiName]"
                        :options="booleans"
                        @select="setUpdateValidationValues(field.apiName, $event)"
                        openDirection="below"
                        style="width: 18vw"
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
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="date"
                id="user-input"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'DateTime'">
              <p>
                {{ field.referenceDisplayLabel }}
              </p>
              <input
                type="datetime-local"
                id="start"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="user-input"
                type="number"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'Boolean'">
              <p>{{ field.referenceDisplayLabel }}:</p>

              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="booleans"
                @select="setUpdateValues(field.apiName, $event)"
                openDirection="below"
                style="width: 18vw"
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
        </div>
        <div class="flex-end">
          <button class="add-button" @click="createResource">Create Opportunity</button>
          <p @click="resetAddOpp" class="cancel">Cancel</p>
        </div>
      </div>
    </Modal>
    <!-- @close-modal="
        () => {
          $emit('cancel'), resetEdit()
        }
      " -->
    <Modal v-if="editOpModalOpen" dimmed>
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3>Update Opportunity</h3>
          </div>
          <img
            src="@/assets/images/close.svg"
            style="height: 1.5rem; margin-top: -1rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetEdit"
            alt=""
          />
        </div>
        <div class="opp-modal">
          <section :key="i" v-for="(field, i) in oppFormCopy">
            <div v-if="field.apiName === 'meeting_type'">
              <p>Note Title:</p>
              <textarea
                id="user-input"
                cols="30"
                rows="2"
                style="width: 36.5vw; border-radius: 0.2rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div v-else-if="field.apiName === 'meeting_comments'">
              <p>Notes:</p>
              <textarea
                id="user-input"
                cols="30"
                rows="8"
                style="width: 36.5vw; border-radius: 0.2rem"
                @input=";(value = $event.target.value), replaceURLs(value, field.apiName)"
              >
              </textarea>
            </div>
            <div
              v-else-if="
                field.dataType === 'TextArea' || (field.length > 250 && field.dataType === 'String')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <textarea
                id="user-input"
                ccols="30"
                rows="4"
                :placeholder="currentVals[field.apiName]"
                style="width: 36.5vw; border-radius: 0.4rem; padding: 7px"
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
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="user-input"
                type="text"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'Boolean'">
              <p>{{ field.referenceDisplayLabel }}:</p>

              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="booleans"
                @select="setUpdateValues(field.apiName, $event)"
                openDirection="below"
                style="width: 18vw"
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
            <div v-else-if="field.apiName === 'AccountId'">
              <p>{{ field.referenceDisplayLabel }}</p>
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
                style="width: 18vw"
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
                (field.dataType === 'Reference' && field.apiName !== 'AccountId')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="
                  field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                    ? picklistQueryOpts[field.apiName]
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
                    ? getReferenceFieldList(field.apiName, field.id, 'update', $event)
                    : null
                "
                :loading="dropdownLoading"
                openDirection="below"
                style="width: 18vw"
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
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more">
                    Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    {{
                      field.apiName === 'AccountId'
                        ? currentAccount
                        : field.apiName === 'OwnerId'
                        ? currentOwner
                        : `${currentVals[field.apiName]}` !== 'null'
                        ? `${currentVals[field.apiName]}`
                        : `${field.referenceDisplayLabel}`
                    }}
                  </p>
                </template>
              </Multiselect>
              <div
                :class="stageGateField ? 'adding-stage-gate' : 'hide'"
                v-if="field.apiName === 'StageName'"
              >
                <div class="adding-stage-gate__header">
                  <img src="@/assets/images/warning.svg" alt="" />
                  <p>This Stage has validation rules</p>
                </div>
                <div class="adding-stage-gate__body">
                  <div v-for="(field, i) in stageValidationFields[stageGateField]" :key="i">
                    <div
                      v-if="
                        field.dataType === 'Picklist' ||
                        field.dataType === 'MultiPicklist' ||
                        (field.dataType === 'Reference' && field.apiName !== 'AccountId')
                      "
                    >
                      <p>{{ field.referenceDisplayLabel }}:</p>
                      <Multiselect
                        :options="
                          field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                            ? stagePicklistQueryOpts[field.apiName]
                            : referenceOpts[field.apiName]
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
                        openDirection="below"
                        v-model="dropdownVal[field.apiName]"
                        style="width: 18vw"
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
                          <p class="multi-slot">No results.</p>
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
                    <div v-else-if="field.apiName === 'AccountId'">
                      <p>{{ field.referenceDisplayLabel }}*</p>
                      <Multiselect
                        v-model="selectedAccount"
                        :options="allAccounts"
                        @search-change="getAccounts($event)"
                        @select="setUpdateValidationValues(field.apiName, $event.id)"
                        openDirection="below"
                        style="width: 18vw"
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
                    <div v-else-if="field.dataType === 'String' && field.apiName !== 'NextStep'">
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
                      <textarea
                        id="user-input"
                        ccols="30"
                        rows="2"
                        :placeholder="currentVals[field.apiName]"
                        style="width: 20vw; border-radius: 6px; padding: 7px"
                        v-model="currentVals[field.apiName]"
                        @input="
                          ;(value = $event.target.value),
                            setUpdateValidationValues(field.apiName, value)
                        "
                      >
                      </textarea>
                    </div>
                    <div v-else-if="field.dataType === 'Date'">
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
                        field.dataType === 'Currency'
                      "
                    >
                      <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
                      <p>{{ field.referenceDisplayLabel }}:</p>

                      <Multiselect
                        v-model="dropdownVal[field.apiName]"
                        :options="booleans"
                        @select="setUpdateValidationValues(field.apiName, $event)"
                        openDirection="below"
                        style="width: 18vw"
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
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }}:</p>
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
            <div v-else-if="field.dataType === 'DateTime'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="datetime-local"
                id="start"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="user-input"
                type="number"
                v-model="currentVals[field.apiName]"
                :placeholder="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
          </section>
        </div>
        <div class="flex-end-opp">
          <div style="display: flex; align-items: center">
            <button @click="updateResource()" class="add-button__">Update</button>
            <p @click="resetEdit" class="cancel">Cancel</p>
          </div>
        </div>
      </div>
    </Modal>

    <div ref="pipelines" v-if="!loading">
      <section class="flex-row-spread">
        <div v-if="!workflowCheckList.length && !primaryCheckList.length" class="flex-row">
          <button @click.stop="showList = !showList" class="select-btn1">
            {{ currentList }}
            <img
              v-if="!showList"
              style="height: 0.7rem; margin-left: 0.5rem"
              src="@/assets/images/rightArrow.svg"
              class="invert"
              alt=""
            />
            <img
              v-else
              class="invert"
              style="height: 0.7rem; margin-left: 0.5rem"
              src="@/assets/images/downArrow.svg"
              alt=""
            />
          </button>
          <div v-outside-click="closeListSelect" v-show="showList" class="list-section">
            <div class="list-section__title flex-row-spread">
              <p>{{ currentList }}</p>
            </div>
            <p @click="showPopularList = !showPopularList" class="list-section__sub-title">
              Standard Lists
              <img
                v-if="showPopularList"
                class="invert"
                src="@/assets/images/downArrow.svg"
                alt=""
              /><img v-else src="@/assets/images/rightArrow.svg" class="invert" alt="" />
            </p>
            <router-link style="width: 100%" v-bind:to="'/pipelines/'">
              <button v-if="showPopularList" @click="allOpportunities" class="list-button">
                All Opportunities
                <span
                  class="filter"
                  v-if="currentList === 'All Opportunities' && !currentWorkflowName"
                >
                  active</span
                >
              </button>
            </router-link>
            <button v-if="showPopularList" @click="closeDatesThisMonth" class="list-button">
              Closing this month
              <span
                class="filter"
                v-if="currentList === 'Closing this month' && !currentWorkflowName"
              >
                active</span
              >
            </button>
            <button v-if="showPopularList" @click="closeDatesNextMonth" class="list-button">
              Closing next month
              <span
                class="filter"
                v-if="currentList === 'Closing next month' && !currentWorkflowName"
              >
                active</span
              >
            </button>
          </div>

          <!-- <button @click.stop="workList = !workList" class="select-btn">
            {{ currentWorkflowName ? currentWorkflowName : 'Active Workflows' }}
            <img
              v-if="!workList"
              style="height: 0.7rem; margin-left: 0.5rem"
              src="@/assets/images/rightArrow.svg"
              class="invert"
              alt=""
            />
            <img
              v-else
              style="height: 0.7rem; margin-left: 0.5rem"
              class="invert"
              src="@/assets/images/downArrow.svg"
              alt=""
            />
          </button>
          <div v-outside-click="closeWorkSelect" v-show="workList" class="work-section">
            <div class="work-section__title flex-row-spread">
              <p>{{ currentWorkflowName ? currentWorkflowName : 'Active Workflows' }}</p>
            </div>
            <p @click="showWorkflowList = !showWorkflowList" class="work-section__sub-title">
              Workflows
              <img
                v-if="showWorkflowList"
                class="invert"
                src="@/assets/images/downArrow.svg"
                alt=""
              /><img v-else src="@/assets/images/rightArrow.svg" class="invert" alt="" />
            </p>
            <div style="width: 100%" v-if="showWorkflowList">
              <div :key="i" v-for="(template, i) in templates.list">
                <button
                  class="list-button"
                  @click="
                    $router.replace({
                      name: 'Pipelines',
                      params: { id: template.id, title: template.title },
                    }),
                      selectList(template.id)
                  "
                >
                  {{ template.title }}
                  <span class="filter" v-if="currentWorkflowName === template.title"> active</span>
                </button>
              </div>
            </div>
          </div> -->
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
              ><img src="@/assets/images/close.svg" @click="removeFilter(filter, i)" alt=""
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
                :dropdowns="picklistQueryOpts"
                :apiName="filterApiName"
                :accounts="allAccounts"
                :owners="allUsers"
              />
            </div>
          </section>

          <section style="position: relative">
            <button
              v-if="activeFilters.length < 4"
              @click.stop="addingFilter"
              class="add-filter-button"
            >
              <img
                src="@/assets/images/plusOne.svg"
                class="invert"
                style="height: 0.8rem; margin-right: 0.25rem"
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
            <div v-if="!closeDateSelected && !advanceStageSelected && !forecastSelected">
              <div class="flex-row">
                <button @click="closeDateSelected = !closeDateSelected" class="select-btn1">
                  Push Close Date
                  <img
                    src="@/assets/images/date.svg"
                    height="14px"
                    style="margin-left: 0.25rem"
                    alt=""
                  />
                </button>
                <button @click="advanceStageSelected = !advanceStageSelected" class="select-btn1">
                  Advance Stage
                  <img
                    src="@/assets/images/stairs.svg"
                    height="14px"
                    style="margin-left: 0.25rem"
                    alt=""
                  />
                </button>
                <button @click="forecastSelected = !forecastSelected" class="select-btn1">
                  Change Forecast
                  <img
                    src="@/assets/images/monetary.svg"
                    height="14px"
                    style="margin-left: 0.25rem"
                    alt=""
                  />
                </button>
                <button @click="modifyForecast('add')" class="select-btn">Start Tracking</button>
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
                v-if="picklistQueryOpts['StageName']"
                :options="picklistQueryOpts['StageName']"
                @select="setStage($event.value)"
                v-model="dropdownVal['StageName']"
                openDirection="below"
                :loading="dropdownLoading"
                style="width: 14vw"
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
                    Select Stage
                  </p>
                </template>
              </Multiselect>
              <p v-else>Add Stage to your update form</p>
              <button
                v-if="picklistQueryOpts['StageName']"
                @click="advanceStage()"
                class="add-button"
              >
                Advance Stage
              </button>
            </div>
            <div class="flex-row-pad" v-if="forecastSelected">
              <p style="font-size: 14px">Select Forecast:</p>
              <Multiselect
                v-if="picklistQueryOpts['ForecastCategoryName']"
                :options="picklistQueryOpts['ForecastCategoryName']"
                @select="setForecast($event.value)"
                v-model="dropdownVal['ForecastCategoryName']"
                openDirection="below"
                :loading="dropdownLoading"
                style="width: 14vw"
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
                    Forecast Category
                  </p>
                </template>
              </Multiselect>
              <p v-else>Add Forecast Category to your update form</p>
              <button
                v-if="picklistQueryOpts['ForecastCategoryName']"
                @click="changeForecast(currentCheckList)"
                class="add-button"
              >
                Change Forecast
              </button>
            </div>
          </div>
          <div class="bulk-action" v-else>
            <SkeletonBox width="400px" height="22px" />
          </div>
        </div>
        <div class="flex-row">
          <div v-if="!selectedWorkflow" class="search-bar">
            <input
              type="search"
              v-model="filterText"
              @input="getFilteredOpps"
              placeholder="search"
            />
            <img src="@/assets/images/search.svg" style="height: 1rem" alt="" />
          </div>
          <div v-else class="search-bar">
            <input type="search" v-model="workflowFilterText" placeholder="search" />
            <img src="@/assets/images/search.svg" style="height: 1rem" alt="" />
          </div>
          <button @click="createOppInstance()" class="add-button">
            <img
              src="@/assets/images/plusOne.svg"
              class="fullInvert"
              style="height: 0.8rem"
              alt=""
            />
            Create Opportunity
          </button>
          <button @click="manualSync" class="select-btn">
            <img src="@/assets/images/refresh.svg" style="height: 1.15rem" alt="" />
          </button>
        </div>
      </section>

      <div class="adding-stage-gate2" v-if="stageFormOpen">
        <div class="adding-stage-gate2__header">
          <div>
            <img src="@/assets/images/warning.svg" alt="" />
            <p>This Stage has validation rules</p>
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
              <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
              <Multiselect
                :options="
                  field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                    ? stagePicklistQueryOpts[field.apiName]
                    : referenceOpts[field.apiName]
                "
                @select="
                  setUpdateValidationValues(
                    field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                    field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'
                      ? $event.value
                      : $event.id,
                  )
                "
                openDirection="below"
                v-model="dropdownVal[field.apiName]"
                style="width: 18vw"
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
                  <p class="multi-slot">No results.</p>
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
            <div v-else-if="field.apiName === 'AccountId'">
              <p>{{ field.referenceDisplayLabel }}*</p>
              <Multiselect
                v-model="selectedAccount"
                :options="allAccounts"
                @search-change="getAccounts($event)"
                @select="setUpdateValidationValues(field.apiName, $event.id)"
                openDirection="below"
                style="width: 18vw"
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
            <div v-else-if="field.dataType === 'String' && field.apiName !== 'NextStep'">
              <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
              <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
              <textarea
                id="user-input"
                ccols="30"
                rows="2"
                :placeholder="currentVals[field.apiName]"
                style="width: 20vw; border-radius: 6px; padding: 7px"
                v-model="currentVals[field.apiName]"
                @input="
                  ;(value = $event.target.value), setUpdateValidationValues(field.apiName, value)
                "
              >
              </textarea>
            </div>
            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
              <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
                field.dataType === 'Currency'
              "
            >
              <p>{{ field.referenceDisplayLabel }} <span>*</span></p>
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
              <p>{{ field.referenceDisplayLabel }}:</p>

              <Multiselect
                v-model="dropdownVal[field.apiName]"
                :options="booleans"
                @select="setUpdateValidationValues(field.apiName, $event)"
                openDirection="below"
                style="width: 18vw"
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
          </div>
        </div>
        <div class="flex-end-opp">
          <div style="display: flex; align-items: center">
            <div v-if="dropdownLoading">
              <PipelineLoader />
            </div>
            <button v-else @click="updateStageForm()" class="add-button__">Update</button>
          </div>
        </div>
      </div>

      <div class="results">
        <h6 style="color: #9b9b9b">
          {{ !currentWorkflowName ? currentList : currentWorkflowName }}:
          <span>{{ selectedWorkflow ? currentWorkflow.length : oppTotal }}</span>
        </h6>
      </div>

      <section v-if="!selectedWorkflow && !loadingWorkflows" class="table-section">
        <div v-outside-click="emitCloseEdit" class="table">
          <PipelineHeader
            :oppFields="oppFields"
            @check-all="onCheckAll"
            @sort-opps="sortOpps"
            @set-opps="setOpps"
            @sort-opps-reverse="sortOppsReverse"
            :allSelected="allSelected"
          />
          <PipelineTableRow
            ref="pipelineTableChild"
            :key="i"
            v-for="(opp, i) in allOpps"
            @create-form="createFormInstance(opp.id, opp.integration_id)"
            @get-notes="getNotes(opp.id)"
            @checked-box="selectPrimaryCheckbox"
            @inline-edit="inlineUpdate"
            @open-stage-form="openStageForm"
            @current-inline-row="changeCurrentRow"
            :closeEdit="closeInline"
            :stages="stagesWithForms"
            :inlineLoader="inlineLoader"
            :picklistOpts="picklistQueryOpts"
            :opp="opp"
            :index="i"
            :oppFields="oppFields"
            :primaryCheckList="primaryCheckList"
            :updateList="updateList"
            :stageData="newStage"
            :closeDateData="daysForward"
            :ForecastCategoryNameData="newForecast"
            :currentInlineRow="currentInlineRow"
          />
        </div>
      </section>

      <section
        v-if="selectedWorkflow && currentWorkflow.length > 0 && !loadingWorkflows"
        class="table-section"
      >
        <div v-outside-click="emitCloseEdit" class="table">
          <WorkflowHeader
            :oppFields="oppFields"
            @check-all="onCheckAllWorkflows"
            :allWorkflowsSelected="allWorkflowsSelected"
            @sort-opps-workflows="sortWorkflows"
            @sort-opps-reverse-workflows="sortWorkflowsReverse"
          />
          <WorkflowRow
            :key="i"
            ref="workflowTableChild"
            v-for="(workflow, i) in filteredWorkflows"
            @create-form="createFormInstance(workflow.id)"
            @get-notes="getNotes(workflow.id)"
            @checked-box="selectWorkflowCheckbox(workflow.id)"
            @inline-edit="inlineUpdate"
            @open-stage-form="openStageForm"
            @current-inline-row="changeCurrentRow"
            :closeEdit="closeInline"
            :stages="stagesWithForms"
            :inlineLoader="inlineLoader"
            :picklistOpts="picklistQueryOpts"
            :workflow="workflow"
            :index="i + 1 * 1000"
            :oppFields="oppFields"
            :workflowCheckList="workflowCheckList"
            :updateWorkflowList="updateList"
            :stageData="newStage"
            :closeDateData="daysForward"
            :ForecastCategoryNameData="newForecast"
            :currentInlineRow="currentInlineRow"
          />
        </div>
      </section>
      <section
        v-if="
          currentWorkflow && currentWorkflow.length < 1 && selectedWorkflow && !loadingWorkflows
        "
        class="empty-table-section"
      >
        <div>
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
      <section v-if="loadingWorkflows" class="empty-table-section">
        <div>
          <PipelineLoader />
        </div>
      </section>

      <div class="row between height-s">
        <div class="pagination">
          <h6>
            <span
              >{{ checkStartingPageNumber() }} -
              {{ selectedWorkflow ? currentWorkflow.length : checkEndingPageNumber() }} of
              {{ selectedWorkflow ? currentWorkflow.length : oppTotal }}</span
            >
          </h6>

          <button v-if="hasPrev" @click="prevPage" class="pag-button">
            <img src="@/assets/images/rightArrow.svg" class="rotate" height="12px" alt="" />
          </button>
          <span class="pagination-num">{{ this.currentPage }}</span>
          <!-- <span class="pagination-num2">{{ this.currentPage + 1 }}</span> -->
          <button v-if="hasNext" @click="nextPage" class="pag-button">
            <img src="@/assets/images/rightArrow.svg" height="12px" alt="" />
          </button>
        </div>
      </div>
    </div>
    <div v-if="loading">
      <Loader loaderText="Pulling in your latest Salesforce data" />
    </div>
  </div>
</template>
<script>
import { SObjects, SObjectPicklist } from '@/services/salesforce'
import AlertTemplate from '@/services/alerts/'
import CollectionManager from '@/services/collectionManager'
import SlackOAuth from '@/services/slack'
import PipelineTableRow from '@/components/PipelineTableRow'
import PipelineHeader from '@/components/PipelineHeader'
import User from '@/services/users'

export default {
  name: 'Pipelines',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PipelineTableRow,
    PipelineHeader,
    WorkflowHeader: () => import(/* webpackPrefetch: true */ '@/components/WorkflowHeader'),
    WorkflowRow: () => import(/* webpackPrefetch: true */ '@/components/WorkflowRow'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
    Filters: () => import(/* webpackPrefetch: true */ '@/components/Filters'),
    FilterSelection: () => import(/* webpackPrefetch: true */ '@/components/FilterSelection'),
  },
  data() {
    return {
      integrationId: null,
      hasNext: false,
      hasPrev: false,
      currentPage: 1,
      oppTotal: 0,
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
      inlineResourceId: null,
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
      selectedAccount: null,
      selectedOwner: null,
      currentOwner: null,
      currentAccount: null,
      updatingOpps: false,
      oppInstanceId: null,
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
      selection: false,
      allStages: [],
      allForecasts: [],
      newStage: null,
      newForecast: null,
      originalList: null,
      daysForward: null,
      allOpps: null,
      loading: false,
      loadingAccounts: false,
      accountSobjectId: null,
      dropdownLoading: false,
      loadingWorkflows: false,
      templates: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
      users: CollectionManager.create({ ModelClass: User }),
      currentWorkflow: null,
      selectedWorkflow: false,
      modalOpen: false,
      editOpModalOpen: false,
      addOppModalOpen: false,
      refreshId: null,
      filterText: '',
      workflowFilterText: '',
      currentList: 'All Opportunities',
      alertInstanceId: null,
      showList: false,
      workList: false,
      showWorkflowList: true,
      showPopularList: true,
      notes: [],
      updateOppForm: null,
      oppFormCopy: null,
      createOppForm: null,
      updateContactForm: null,
      oppFields: [],
      instanceId: null,
      contactInstanceId: null,
      formData: {},
      noteTitle: '',
      noteInfo: '',
      referenceOpts: {},
      createReferenceOpts: {},
      picklistQueryOpts: {},
      createQueryOpts: {},
      picklistQueryOptsContacts: {},
      stagePicklistQueryOpts: {},
      setFilters: {},
      instanceIds: [],
      allAccounts: null,
      allUsers: null,
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
      filters: [],
      operatorsLength: 0,
      stageGateId: null,
      forecastList: [],
      stageIntegrationId: null,
      stageId: null,
      allOppsForWorkflows: null,
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
    currentCheckList() {
      if (this.primaryCheckList.length > 0) {
        return this.primaryCheckList
      } else if (this.workflowCheckList.length > 0) {
        return this.workflowCheckList
      } else {
        return []
      }
    },
    user() {
      return this.$store.state.user
    },
    allOppsFiltered() {
      return this.allOpps.filter((opp) =>
        opp.name.toLowerCase().includes(this.filterText.toLowerCase()),
      )
    },
    filteredWorkflows: {
      get: function () {
        return this.currentWorkflow.filter((opp) =>
          opp.name.toLowerCase().includes(this.workflowFilterText.toLowerCase()),
        )
      },
      set: function (newvalue) {
        this.currentWorkflow = newvalue
      },
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
    this.templates.refresh()
    this.getObjects()
    this.getObjectsForWorkflows()
    this.getAllForms()
  },
  beforeMount() {
    this.getUsers()
  },
  mounted() {
    this.selectList()
    this.resourceSync()
  },
  watch: {
    primaryCheckList: 'closeAll',
    workflowCheckList: 'closeAll',
    stageGateField: 'stageGateInstance',
    updateOppForm: 'setForms',
    currentCheckList: 'addToForecastList',
    accountSobjectId: 'getInitialAccounts',
  },
  methods: {
    async getFilteredOpps() {
      try {
        const res = await SObjects.api.getObjects('Opportunity', 1, true, [
          ['CONTAINS', 'Name', this.filterText.toLowerCase()],
        ])
        console.log(res)
        this.allOpps = res.results
        this.originalList = res.results
        res.next ? (this.hasNext = true) : (this.hasNext = false)
        res.previous ? (this.hasPrev = true) : (this.hasPrev = false)
        this.oppTotal = res.count

        if (this.currentList === 'Closing this month') {
          this.stillThisMonth()
        } else if (this.currentList === 'Closing next month') {
          this.stillNextMonth()
        }
      } catch (e) {
        this.$toast('Error gathering Opportunities!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    checkStartingPageNumber() {
      if (this.currentPage === 1) {
        return this.currentPage
      } else {
        return (this.currentPage - 1) * 20 + 1
      }
    },
    checkEndingPageNumber() {
      let pages = this.oppTotal / 20
      if (pages % 1 !== 0) {
        pages = Math.ceil(pages)
      }
      if (this.currentPage * 20 > this.oppTotal) {
        return this.oppTotal
      } else {
        return this.currentPage * 20
      }
    },
    nextPage() {
      this.getObjects(this.currentPage + 1)
    },
    prevPage() {
      this.getObjects(this.currentPage - 1)
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
      console.log(message)
      this.setUpdateValues(field, message)
    },
    changeCurrentRow(i) {
      this.currentInlineRow = i
    },
    addToForecastList() {
      let list = []
      for (let i = 0; i < this.currentCheckList.length; i++) {
        list.push(this.allOpps.filter((opp) => opp.id === this.currentCheckList[i])[0])
      }
      this.forecastList = list.map((opp) => opp.integration_id)
    },
    async modifyForecast(action) {
      try {
        await User.api.modifyForecast(action, this.forecastList)

        this.$toast('Opportunities added to Tracker.', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error adding opportunities.', {
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
    openStageForm(field, id, integrationId) {
      this.setUpdateValues('StageName', field)
      this.stageGateField = field
      this.stageFormOpen = true
      this.stageId = id
      this.stageIntegrationId = integrationId
      // this.stageGateInstance(field)
      // this.oppInstance(id)
    },
    closeStageForm() {
      this.stageFormOpen = false
      this.stageGateField = null
      this.resource_id = null
      this.stageId = null
      this.stageIntegrationId = null
    },
    async getReferenceFieldList(key, val, type, eventVal) {
      try {
        const res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: val,
          value: eventVal ? eventVal : '',
        })
        if (type === 'update') {
          this.referenceOpts[key] = res
        } else {
          this.createReferenceOpts[key] = res
        }
      } catch (e) {
        this.$toast('Error gathering reference fields', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    emitCloseEdit() {
      this.closeInline += 1
    },
    async inlineUpdate(formData, id, integrationId) {
      this.inlineLoader = true
      try {
        const res = await SObjects.api
          .updateResource({
            form_data: formData,
            resource_type: 'Opportunity',
            form_type: 'UPDATE',
            resource_id: id,
            integration_ids: [integrationId],
            from_workflow: this.selectedWorkflow ? true : false,
            workflow_title: this.selectedWorkflow ? this.currentWorkflowName : 'None',
          })
          .then(async () => {
            if (this.filterText) {
              let updatedRes = await SObjects.api.getObjects('Opportunity', 1, true, [
                ['CONTAINS', 'Name', this.filterText],
              ])
              let wfr = await SObjects.api.getObjectsForWorkflows('Opportunity')
              this.allOppsForWorkflows = wfr.results
              this.allOpps = updatedRes.results
              this.originalList = updatedRes.results
              updatedRes.next ? (this.hasNext = true) : (this.hasNext = false)
              updatedRes.previous ? (this.hasPrev = true) : (this.hasPrev = false)
              this.oppTotal = updatedRes.count
              this.currentPage = 1
            } else {
              let updatedRes = await SObjects.api.getObjects('Opportunity', 1)
              let wfr = await SObjects.api.getObjectsForWorkflows('Opportunity')
              this.allOppsForWorkflows = wfr.results
              this.allOpps = updatedRes.results
              this.originalList = updatedRes.results
              updatedRes.next ? (this.hasNext = true) : (this.hasNext = false)
              updatedRes.previous ? (this.hasPrev = true) : (this.hasPrev = false)
              this.oppTotal = updatedRes.count
              this.currentPage = 1
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
          })
        this.$toast('Salesforce Update Successful', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.inlineLoader = false
          this.closeInline += 1
        }, 1000)
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
      this.filters = []
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
        const res = await SObjects.api.getObjects('Opportunity', 1, true, this.filters)
        if (this.selectedWorkflow) {
          this.allOpps = res.results
          this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
        } else if (this.currentList === 'Closing this month') {
          this.allOpps = res.results
          this.allOpps = this.allOpps.filter(
            (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth,
          )
        } else if (this.currentList === 'Closing next month') {
          this.allOpps = res.results
          this.allOpps = this.allOpps.filter(
            (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth + 1,
          )
        } else {
          this.allOpps = res.results
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
      // if (this.currentOperators.length < this.operatorsLength) {
      //   this.currentOperators.push('equals')
      // }
      this.getFilteredObjects(value)
      this.filterSelected = false
      this.activeFilters.push(this.currentFilter)
    },
    valueSelected(value, name) {
      let users = this.allUsers.filter((user) => user.salesforce_account_ref)
      let user = null
      if (name === 'OwnerId') {
        user = users.filter((user) => user.salesforce_account_ref.salesforce_id === value)
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
      this.activeFilters.splice(index, 1)
      this.filters.splice(index, 1)
      this.filterValues.splice(index, 1)
      this.currentOperators.splice(index, 1)
      this.getFilteredObjects()
      if (this.activeFilters.length < 1) {
        this.updateOpps()
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

      if (field === 'Stage') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data']['StageName']
          const nameB = b['secondary_data']['StageName']
          return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
        })
      } else if (field === 'Last Activity') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}` + 'Date']
          const nameB = b['secondary_data'][`${newField}` + 'Date']
          return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
        })
      } else if (dT === 'TextArea' && !apiName.includes('__c')) {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]

          return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
        })
      } else if (apiName.includes('__c') && dT !== 'TextArea') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${apiName}`]
          const nameB = b['secondary_data'][`${apiName}`]
          return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
        })
      } else if (apiName.includes('__c') && dT === 'TextArea') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${apiName}`]
          const nameB = b['secondary_data'][`${apiName}`]
          return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
        })
      } else {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
        })
      }
    },
    sortOppsReverse(dT, field, apiName) {
      let newField = this.capitalizeFirstLetter(this.camelize(field))

      if (field === 'Stage') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data']['StageName']
          const nameB = b['secondary_data']['StageName']
          return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
        })
      } else if (field === 'Last Activity') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}` + 'Date']
          const nameB = b['secondary_data'][`${newField}` + 'Date']
          return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
        })
      } else if (dT === 'TextArea' && !apiName.includes('__c')) {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
        })
      } else if (apiName.includes('__c') && dT !== 'TextArea') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${apiName}`]
          const nameB = b['secondary_data'][`${apiName}`]
          return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
        })
      } else if (apiName.includes('__c') && dT === 'TextArea') {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${apiName}`]
          const nameB = b['secondary_data'][`${apiName}`]
          return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
        })
      } else {
        this.allOpps = this.allOpps.sort(function (a, b) {
          const nameA = a['secondary_data'][`${newField}`]
          const nameB = b['secondary_data'][`${newField}`]
          return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
        })
      }
    },
    sortWorkflows(dT, field, apiName) {
      let newField = this.capitalizeFirstLetter(this.camelize(field))

      if (field === 'Stage') {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data']['StageName']
          const nameB = b['secondary_data']['StageName']
          return (nameB === null) - (nameA === null) || -(nameB > nameA) || +(nameB < nameA)
        })
      } else if (field === 'Last Activity') {
        this.allOpps = this.allOpps.sort(function (a, b) {
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
        this.allOpps = this.allOpps.sort(function (a, b) {
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
    },
    sortWorkflowsReverse(dT, field, apiName) {
      let newField = this.capitalizeFirstLetter(this.camelize(field))
      if (field === 'Stage') {
        this.currentWorkflow = this.currentWorkflow.sort(function (a, b) {
          const nameA = a['secondary_data']['StageName']
          const nameB = b['secondary_data']['StageName']
          return (nameA === null) - (nameB === null) || -(nameA > nameB) || +(nameA < nameB)
        })
      } else if (field === 'Last Activity') {
        this.allOpps = this.allOpps.sort(function (a, b) {
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
        this.allOpps = this.allOpps.sort(function (a, b) {
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
    },
    selectPrimaryCheckbox(id, index) {
      if (this.primaryCheckList.includes(id)) {
        this.primaryCheckList = this.primaryCheckList.filter((opp) => opp !== id)
      } else {
        this.primaryCheckList.push(id)
      }

      // if (this.selectedRows.includes(index)) {
      //   this.selectedRows = this.selectedRows.filter((i) => i !== index)
      // } else {
      //   this.selectedRows.push(index)
      // }
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
      }
    },
    setStage(val) {
      this.newStage = val
    },
    setForecast(val) {
      this.newForecast = val
    },
    onCheckAll() {
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
    },
    onCheckAllWorkflows() {
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
    },
    async listPicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.picklistQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        this.$toast('Error gathering update picklist fields', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async listStagePicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.stagePicklistQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        this.$toast('Error gathering stage picklist fields', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async listCreatePicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.createQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        this.$toast("Error gathering 'create' picklist fields", {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
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
    },
    resetAddOpp() {
      this.addOppModalOpen = !this.addOppModalOpen
    },
    async updateContactInstance() {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Contact',
          formType: 'UPDATE',
        })
        // this.addOppModalOpen = true
        this.contactInstanceId = res.form_id
      } catch (e) {
        this.$toast('Error updating conacts', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async createFormInstance(id, integrationId, alertInstanceId = null) {
      this.formData = {}
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
      this.alertInstanceId = alertInstanceId
      this.oppId = id
      try {
        const res = await SObjects.api.getCurrentValues({
          resourceType: 'Opportunity',
          resourceId: id,
        })
        this.currentVals = res.current_values
        this.currentOwner = this.allUsers.filter(
          (user) => user.salesforce_account_ref.salesforce_id === this.currentVals['OwnerId'],
        )[0].full_name
        this.allOppsForWorkflows.filter((opp) => opp.id === this.oppId)[0].account_ref
          ? (this.currentAccount = this.allOpps.filter(
              (opp) => opp.id === this.oppId,
            )[0].account_ref.name)
          : (this.currentAccount = 'Account')
      } catch (e) {
        this.$toast('Error creating update form, close modal and try again.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.dropdownLoading = false
      }
    },
    async createOppInstance() {
      this.formData = {}
      this.currentVals = []
      this.selectedAccount = null
      this.selectedOwner = null
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'CREATE',
        })
        this.addOppModalOpen = true
        this.oppInstanceId = res.form_id
      } catch (e) {
        this.$toast('Error building create form', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async oppInstance(id) {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'UPDATE',
          resourceId: id,
        })
        this.currentVals = res.current_values
        this.oppInstanceId = res.form_id
      } catch (e) {
        this.$toast('Error building update form, close modal and try again.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async stageGateInstance(field) {
      this.stageGateId = null
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
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
          // this.updateWorkflowList(this.currentWorkflowName, this.refreshId)
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
    setUpdateValues(key, val, multi) {
      if (multi) {
        this.formData[key] = this.formData[key] ? this.formData[key] + ';' + val : val
      }

      if (val && !multi) {
        this.formData[key] = val
      }
      if (key === 'StageName') {
        this.stagesWithForms.includes(val)
          ? (this.stageGateField = val)
          : (this.stageGateField = null)
      }
    },
    setUpdateValidationValues(key, val) {
      if (val) {
        this.formData[key] = val
      }
    },
    async updateOpps() {
      try {
        let updatedRes = await SObjects.api.getObjects('Opportunity')
        this.allOpps = updatedRes.results
        this.originalList = updatedRes.results
        if (this.currentList === 'Closing this month') {
          this.stillThisMonth()
        } else if (this.currentList === 'Closing next month') {
          this.stillNextMonth()
        }
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
      if (this.currentDay !== this.syncDay) {
        setTimeout(() => {
          this.loading = true
        }, 300)
        try {
          await SObjects.api.resourceSync()
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
          this.$toast('Daily sync complete', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      }
    },
    async manualSync() {
      try {
        await SObjects.api.resourceSync()
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
        this.$toast('Sync complete', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async updateStageForm() {
      this.dropdownLoading = true
      try {
        const res = await SObjects.api
          .updateResource({
            form_data: this.formData,
            resource_type: 'Opportunity',
            form_type: 'UPDATE',
            resource_id: this.stageId,
            integration_ids: [this.stageIntegrationId],
            stage_name: this.stageGateField ? this.stageGateField : null,
          })
          .then(async () => {
            if (this.filterText) {
              let updatedRes = await SObjects.api.getObjects('Opportunity', 1, true, [
                ['CONTAINS', 'Name', this.filterText],
              ])
              let wfr = await SObjects.api.getObjectsForWorkflows('Opportunity')
              this.allOppsForWorkflows = wfr.results
              this.allOpps = updatedRes.results
              this.originalList = updatedRes.results
              updatedRes.next ? (this.hasNext = true) : (this.hasNext = false)
              updatedRes.previous ? (this.hasPrev = true) : (this.hasPrev = false)
              this.oppTotal = updatedRes.count
              this.currentPage = 1
            } else {
              let updatedRes = await SObjects.api.getObjects('Opportunity', 1)
              let wfr = await SObjects.api.getObjectsForWorkflows('Opportunity')
              this.allOppsForWorkflows = wfr.results
              this.allOpps = updatedRes.results
              this.originalList = updatedRes.results
              updatedRes.next ? (this.hasNext = true) : (this.hasNext = false)
              updatedRes.previous ? (this.hasPrev = true) : (this.hasPrev = false)
              this.oppTotal = updatedRes.count
              this.currentPage = 1
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
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.closeStageForm()
        this.formData = {}
        this.dropdownLoading = false
        this.$toast('Salesforce Update Successful', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async updateResource() {
      this.updateList.push(this.oppId)
      this.editOpModalOpen = false
      try {
        const res = await SObjects.api
          .updateResource({
            // form_id: this.stageGateField ? [this.instanceId, this.stageGateId] : [this.instanceId],
            form_data: this.formData,
            from_workflow: this.selectedWorkflow ? true : false,
            workflow_title: this.selectedWorkflow ? this.currentWorkflowName : 'None',
            form_type: 'UPDATE',
            integration_ids: [this.integrationId],
            resource_type: 'Opportunity',
            resource_id: this.oppId,
            stage_name: this.stageGateField ? this.stageGateField : null,
          })
          .then(async () => {
            if (this.filterText) {
              let updatedRes = await SObjects.api.getObjects('Opportunity', 1, true, [
                ['CONTAINS', 'Name', this.filterText],
              ])
              let wfr = await SObjects.api.getObjectsForWorkflows('Opportunity')
              this.allOppsForWorkflows = wfr.results
              this.allOpps = updatedRes.results
              this.originalList = updatedRes.results
              updatedRes.next ? (this.hasNext = true) : (this.hasNext = false)
              updatedRes.previous ? (this.hasPrev = true) : (this.hasPrev = false)
              this.oppTotal = updatedRes.count
              this.currentPage = 1
            } else {
              let updatedRes = await SObjects.api.getObjects('Opportunity', 1)
              let wfr = await SObjects.api.getObjectsForWorkflows('Opportunity')
              this.allOppsForWorkflows = wfr.results
              this.allOpps = updatedRes.results
              this.originalList = updatedRes.results
              updatedRes.next ? (this.hasNext = true) : (this.hasNext = false)
              updatedRes.previous ? (this.hasPrev = true) : (this.hasPrev = false)
              this.oppTotal = updatedRes.count
              this.currentPage = 1
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
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.updateList = []
        this.formData = {}
        this.closeFilterSelection()
        this.$toast('Salesforce Update Successful', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async createResource() {
      this.addOppModalOpen = false
      try {
        await SObjects.api
          .createResource({
            form_id: this.oppInstanceId,
            form_data: this.formData,
          })
          .then(async () => {
            let updatedRes = await SObjects.api.getObjects('Opportunity')
            this.allOpps = updatedRes.results
            this.originalList = updatedRes.results
          })
      } catch (e) {
        this.$toast('Error creating opportunity', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.$toast('Opportunity created successfully.', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async selectList(id) {
      if (this.id) {
        this.loadingWorkflows = true
        this.refreshId = id ? id : this.id
        try {
          let res = await AlertTemplate.api.runAlertTemplateNow(id ? id : this.id, {
            fromWorkflow: true,
          })
          this.currentWorkflow = this.allOppsForWorkflows.filter((opp) =>
            res.data.ids.includes(opp.integration_id),
          )
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
          this.selectedWorkflow = true
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
        this.currentWorkflow = this.allOppsForWorkflows.filter((opp) =>
          res.data.ids.includes(opp.integration_id),
        )
        this.filteredWorkflows = this.currentWorkflow
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
      }
    },
    setForms() {
      for (let i in this.picklistQueryOptsContacts) {
        this.picklistQueryOptsContacts[i] = this.listPicklists(i, {
          picklistFor: i,
          salesforceObject: 'Opportunity',
        })
      }

      for (let i = 0; i < this.oppFormCopy.length; i++) {
        if (
          this.oppFormCopy[i].dataType === 'Picklist' ||
          this.oppFormCopy[i].dataType === 'MultiPicklist'
        ) {
          this.picklistQueryOpts[this.oppFormCopy[i].apiName] = this.oppFormCopy[i].apiName
        } else if (this.oppFormCopy[i].dataType === 'Reference') {
          this.referenceOpts[this.oppFormCopy[i].apiName] = this.oppFormCopy[i].id
        }
      }

      for (let i in this.picklistQueryOpts) {
        this.picklistQueryOpts[i] = this.listPicklists(i, {
          picklistFor: i,
          salesforceObject: 'Opportunity',
        })
      }

      for (let i in this.referenceOpts) {
        this.referenceOpts[i] = this.getReferenceFieldList(i, this.referenceOpts[i], 'update')
      }

      for (let i = 0; i < this.createOppForm.length; i++) {
        if (
          this.createOppForm[i].dataType === 'Picklist' ||
          this.createOppForm[i].dataType === 'MultiPicklist'
        ) {
          this.createQueryOpts[this.createOppForm[i].apiName] = this.createOppForm[i].apiName
        } else if (this.createOppForm[i].dataType === 'Reference') {
          this.createReferenceOpts[this.createOppForm[i].apiName] = this.createOppForm[i].id
        }
      }

      for (let i in this.createQueryOpts) {
        this.createQueryOpts[i] = this.listCreatePicklists(i, {
          picklistFor: i,
          salesforceObject: 'Opportunity',
        })
      }

      for (let i in this.createReferenceOpts) {
        this.createReferenceOpts[i] = this.getReferenceFieldList(
          i,
          this.createReferenceOpts[i],
          'create',
        )
      }

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
          field.apiName !== 'AccountId' &&
          field.apiName !== 'OwnerId',
      )

      for (let i in this.stagePicklistQueryOpts) {
        this.stagePicklistQueryOpts[i] = this.listStagePicklists(i, {
          picklistFor: i,
          salesforceObject: 'Opportunity',
        })
      }
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()

        this.updateOppForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Opportunity',
        )
        this.createOppForm = res.filter(
          (obj) => obj.formType === 'CREATE' && obj.resource === 'Opportunity',
        )
        let stageGateForms = res.filter(
          (obj) => obj.formType === 'STAGE_GATING' && obj.resource === 'Opportunity',
        )

        let stages = stageGateForms.map((field) => field.stage)
        this.stagesWithForms = stages
        this.oppFormCopy = this.updateOppForm[0].fieldsRef
        this.createOppForm = this.createOppForm[0].fieldsRef.filter(
          (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
        )

        for (const field of stageGateForms) {
          this.stageValidationFields[field.stage] = field.fieldsRef
        }
        let stageArrayOfArrays = stageGateForms.map((field) => field.fieldsRef)
        let allStageFields = [].concat.apply([], stageArrayOfArrays)
        let dupeStagesRemoved = [
          ...new Map(allStageFields.map((v) => [v.referenceDisplayLabel, v])).values(),
        ]

        for (let i = 0; i < dupeStagesRemoved.length; i++) {
          if (
            dupeStagesRemoved[i].dataType === 'Picklist' ||
            dupeStagesRemoved[i].dataType === 'MultiPicklist'
          ) {
            this.stagePicklistQueryOpts[dupeStagesRemoved[i].apiName] = dupeStagesRemoved[i].apiName
          } else if (dupeStagesRemoved[i].dataType === 'Reference') {
            this.stagePicklistQueryOpts[dupeStagesRemoved[i].referenceDisplayLabel] =
              dupeStagesRemoved[i].referenceDisplayLabel
          }
        }
      } catch (error) {
        this.$toast('Error setting form fields!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getUsers() {
      try {
        const res = await SObjects.api.getObjects('User')
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
    async getObjectsForWorkflows() {
      this.loading = true
      try {
        const res = await SObjects.api.getObjectsForWorkflows('Opportunity')
        this.allOppsForWorkflows = res.results
      } catch (e) {
        this.$toast('Error gathering Opportunities!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        setTimeout(() => {
          this.loading = false
        }, 100)
      }
    },
    async getObjects(page = 1) {
      this.currentPage = page
      this.loading = true
      try {
        const res = await SObjects.api.getObjects('Opportunity', page)
        this.allOpps = res.results
        this.originalList = res.results
        res.next ? (this.hasNext = true) : (this.hasNext = false)
        res.previous ? (this.hasPrev = true) : (this.hasPrev = false)
        this.oppTotal = res.count

        if (this.currentList === 'Closing this month') {
          this.stillThisMonth()
        } else if (this.currentList === 'Closing next month') {
          this.stillNextMonth()
        }
      } catch (e) {
        this.$toast('Error gathering Opportunities!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        setTimeout(() => {
          this.loading = false
        }, 100)
      }
    },
    async getNotes(id) {
      try {
        const res = await SObjects.api.getNotes({
          resourceId: id,
        })
        this.modalOpen = true
        if (res.length) {
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
      this.allOpps = this.originalList
      this.selectedWorkflow = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth,
      )
      this.currentList = 'Closing this month'
      this.showList = false
      this.workList = false
      this.closeFilterSelection()
    },
    stillThisMonth() {
      this.allOpps = this.originalList
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth,
      )
      this.currentList = 'Closing this month'
    },
    closeDatesNextMonth() {
      this.allOpps = this.originalList
      this.selectedWorkflow = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth + 1,
      )
      this.currentList = 'Closing next month'
      this.showList = false
      this.closeFilterSelection()
    },
    stillNextMonth() {
      this.allOpps = this.originalList
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.secondary_data.CloseDate).getUTCMonth() == this.currentMonth + 1,
      )
      this.currentList = 'Closing next month'
    },
    allOpportunities() {
      this.selectedWorkflow = false
      this.allOpps = this.originalList
      this.currentList = 'All Opportunities'
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
.adding-product {
  height: 3rem;
  margin: 1rem 0rem;
  display: flex;
  justify-content: center;

  button {
    display: flex;
    flex-direction: row;
    align-items: center;
    color: $dark-green;
    background: transparent;
    padding: none;
    border: none;
    cursor: pointer;
    img {
      height: 1rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.adding-stage-gate2 {
  border: 1px solid $very-light-gray;
  box-shadow: 1px 3px 7px 2px $very-light-gray;
  background-color: white;
  border-radius: 0.3rem;
  margin: 0.5rem 0rem;
  width: 36vw;
  min-height: 50vh;
  left: 32vw;
  top: 18vh;
  position: absolute;
  z-index: 12;
  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    font-size: 16px;
    padding: 0.75rem 0.5rem;
    color: $base-gray;
    width: 100%;
    border-bottom: 1px solid $soft-gray;
    img {
      height: 1rem;
      margin-right: 0.5rem;
    }

    div {
      display: flex;
      align-items: center;
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
      width: 10vw !important;
      height: 1.5rem !important;
    }
    .multiselect {
      width: 12vw !important;
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
.adding-stage-gate {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  margin: 0.5rem 0rem;
  width: 36vw;
  min-height: 30vh;
  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    font-size: 14px;
    padding: 0.5rem;
    color: $base-gray;
    width: 100%;
    border-bottom: 1px solid #e8e8e8;
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
      width: 10vw !important;
      height: 1.5rem !important;
    }
    .multiselect {
      width: 12vw !important;
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
  padding-left: 4px;
  height: 34px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}
.pagination {
  width: 50vw;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  margin: 8px 0px 0px 0px;

  h6 {
    span {
      letter-spacing: 0.5px;
      margin-right: 1rem;
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
    padding: 3px 6px;
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
  &-rotate {
  }
  button {
    margin-right: 8px;
  }
}
.pag-button {
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  padding: 3px;
  font-size: 12px;
  cursor: pointer;
  img {
    filter: invert(60%);
  }
}
.rotate {
  transform: rotate(180deg);
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.height-s {
  height: 36px;
}
.between {
  justify-content: space-between;
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
.select-btn1 {
  border: 0.7px solid $very-light-gray;
  padding: 0.4rem 0.75rem;
  font-size: 12px;
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
.select-btn {
  border: 0.5px solid $dark-green;
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
    height: 1rem !important;
  }
}
.work-btn {
  border: 1px solid #e8e8e8;
  min-height: 4.5vh;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background-color: $base-gray;
  cursor: pointer;
  color: white;
  letter-spacing: 0.2px;
  margin-right: 0.5rem;
  transition: all 0.25s;
}
.select-btn:hover,
.work-btn:hover {
  transform: scale(1.015);
  box-shadow: 1px 1px 2px $very-light-gray;
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
  max-height: 72vh;
  overflow: scroll;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  border-collapse: separate;
  border-spacing: 3px;
  background-color: white;
}
.table-section::-webkit-scrollbar {
  width: 0px; /* Mostly for vertical scrollbars */
  height: 8px; /* Mostly for horizontal scrollbars */
}
.table-section::-webkit-scrollbar-thumb {
  background-image: linear-gradient(100deg, $darker-green 0%, $lighter-green 99%);
  box-shadow: inset 4px 4px 8px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 0.3rem;
}
.table-section::-webkit-scrollbar-track {
  // background: $soft-gray;
  box-shadow: inset 4px 4px 8px 0 $soft-gray;
  border-radius: 0.3rem;
}
.table-section::-webkit-scrollbar-track-piece:end {
  margin-right: 50vw;
}
.green-text {
  color: $dark-green;
  text-decoration: underline;
}
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
.modal-container {
  background-color: $white;
  overflow: auto;
  min-width: 32vw;
  max-width: 36vw;
  min-height: 44vh;
  max-height: 80vh;
  align-items: center;
  border-radius: 0.5rem;
  border: 1px solid $very-light-gray;
  padding: 0px 4px;
}
.close-button {
  border-radius: 50%;
  background-color: white;
  box-shadow: 1px 1px 1px 1px $very-light-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -1rem;
  padding: 0.25rem;
  cursor: pointer;
  img {
    filter: invert(80%);
  }
}
.opp-modal-container {
  overflow: hidden;
  background-color: white;
  // min-height: 80vh;
  width: 40vw;
  align-items: center;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #e8e8e8;
}
.opp-modal {
  width: 40vw;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem;
  overflow: auto;
  max-height: 56vh;
  border-radius: 0.3rem;
  border-bottom: 3px solid $white;
  color: $base-gray;
  font-size: 16px;
  letter-spacing: 0.75px;
  div {
    margin-right: 0.25rem;
  }
}
.note-section {
  padding: 0.25rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  overflow: scroll;
  &__title {
    font-size: 19px;
    font-weight: bolder;
    letter-spacing: 0.6px;
    color: $base-gray;
    padding: 0;
  }
  &__body {
    color: $base-gray;
    font-family: $base-font-family;
    word-wrap: break-word;
    white-space: pre-wrap;
    border-left: 2px solid $dark-green;
    padding-left: 8px;
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
.table-cell-header {
  display: table-cell;
  padding: 1.25vh 3vh;
  border-bottom: 1px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 2;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
}
input[type='search'] {
  border: none;
  background-color: $off-white;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
input[type='text']:focus {
  outline: none;
  cursor: text;
}
input[type='checkbox'] {
  cursor: pointer;
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
  margin: 0.75rem 0rem;
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
.pipelines {
  padding: 4.2rem 1.25rem 0.75rem 0.75rem;
  color: $base-gray;
  margin: 0 1rem 0 0.5rem;
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
}
.add-button:disabled:hover {
  transform: none;
}
.add-filter-button {
  display: flex;
  align-items: center;
  border: none;
  height: 4.5vh;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background-color: transparent;
  cursor: pointer;
  color: $dark-green;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
.add-button {
  display: flex;
  align-items: center;
  border: none;
  margin: 0 0.5rem 0 0;
  padding: 0.4rem 0.75rem;
  font-size: 12px;
  border-radius: 6px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
.add-button:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.add-button__:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.search-bar {
  height: 1.8rem;
  background-color: $off-white;
  border: 0.7px solid $gray;
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 5px;
  margin-right: 0.5rem;
}
#update-input {
  border: none;
  border-radius: 6px;
  box-shadow: 1px 1px 1px 1px $very-light-gray;
  background-color: white;
  min-height: 2.5rem;
  width: 14vw;
}
#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2.5rem;
  width: 18vw;
  font-family: $base-font-family;
}
#user-input:focus {
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
.loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  filter: invert(99%);
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
.work-section {
  z-index: 4;
  position: absolute;
  top: 20vh;
  left: 12.5vw;
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
  &__title {
    position: sticky;
    top: 0;
    z-index: 5;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.25px;
    padding-left: 0.75rem;
    font-weight: bold;
    font-size: 16px;
    width: 100%;
  }
  &__sub-title {
    font-size: 12px;
    letter-spacing: 0.3px;
    font-weight: bold;
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
.list-section {
  z-index: 4;
  position: absolute;
  top: 20vh;
  left: 1rem;
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
  &__title {
    position: sticky;
    top: 0;
    z-index: 5;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.25px;
    padding-left: 0.75rem;
    font-weight: bold;
    font-size: 16px;
    width: 100%;
  }
  &__sub-title {
    font-size: 12px;
    letter-spacing: 0.3px;
    font-weight: bold;
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
  color: $mid-gray;
  cursor: pointer;
  font-size: 11px;
  font-weight: bolder;
}
.list-button:hover {
  color: $dark-green;
  background-color: $off-white;
}
.filter {
  color: #41b883;
  margin-left: 0.2rem;
}
.exit {
  padding-right: 0.75rem;
  margin-top: -0.5rem;
  height: 1rem;
  cursor: pointer;
}
.cancel {
  color: $dark-green;
  font-weight: bold;
  margin-left: 1rem;
  cursor: pointer;
}
.flex-end {
  width: 100%;
  padding: 2rem 0.25rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.flex-end-opp {
  width: 100%;
  padding: 0.5rem 1.5rem;
  height: 5rem;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
}
textarea {
  resize: vertical;
}
a {
  text-decoration: none;
}
.logo {
  height: 20px;
  margin-left: 0.5rem;
  margin-right: 0.25rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.pagination {
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  margin: 4px 0px 0px 0px;
  height: 30px;

  &-num {
    margin-right: 8px;
    font-size: 11px;
  }
  &-rotate {
  }
  button {
    margin-right: 8px;
  }
}
.pag-button {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  border: 1px solid #e8e8e8;
  padding: 2px;
}
.rotate {
  transform: rotate(180deg);
}
</style>