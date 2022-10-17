   <template>
  <div>
    <section class="wrapper">
      <div class="tabs">
        <div class="tab">
          <input type="radio" name="css-tabs" id="tab-1" checked class="tab-switch" />
          <label for="tab-1" class="tab-label">Opportunity</label>
          <div class="tab-content">
            <section>
              <div>
                <p @click="switchFormType" class="form-type">
                  {{ camelize(formType) }} Form Builder
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
          <label for="tab-2" class="tab-label">Stage Related</label>
          <div class="tab-content">
            <p>Stage Gate</p>
          </div>
        </div>
        <div class="tab">
          <input type="radio" name="css-tabs" id="tab-3" class="tab-switch" />
          <label for="tab-3" class="tab-label" @click="changeToAccount">Account</label>
          <div class="tab-content">
            <section>
              <div>
                <p @click="switchFormType" class="form-type">
                  {{ camelize(formType) }} Form Builder
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
          <label for="tab-4" class="tab-label">Contact</label>
          <div class="tab-content">
            <section>
              <div>
                <p @click="switchFormType" class="form-type">
                  {{ camelize(formType) }} Form Builder
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
          <label for="tab-5" class="tab-label">Lead</label>
          <div class="tab-content">
            <section>
              <div>
                <p @click="switchFormType" class="form-type">
                  {{ camelize(formType) }} Form Builder
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
  </div>
</template>
