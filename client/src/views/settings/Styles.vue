<template>
  <div class="page">
    <div class="page__left-nav-bar">
      <div class="toolbar">
        <div class="toolbar__header">
          <span class="toolbar__title">Side Nav Styles</span>
        </div>
      </div>
      <button class="toolbar__button-fullwidth">Full Width Button</button>

      <div class="toolbar">
        <div class="toolbar__header">
          <span class="toolbar__title">
            This is a toolbar
          </span>
        </div>
        <div class="toolbar__row">
          Toolbar element 1
        </div>
        <div class="toolbar__row toolbar__active">
          Toolbar element 2 (active)
        </div>
        <div class="toolbar__row">
          Toolbar element 3
        </div>
      </div>

      <div class="filter-box">
        <div class="filter-box__header">
          <div class="filter-box__title">
            Sort and Filter
          </div>
        </div>
        <div class="filter-box__section">
          <div class="filter-box__section-header">
            <div class="filter-box__section-title">
              Update Date
            </div>
            <div class="filter-box__section-header-icon">
              <img src="@/assets/images/add.svg" alt="add icon" />
            </div>
          </div>
          <div class="filter-box__section-row">
            Feeling Lucky
          </div>
          <div class="filter-box__section-row">
            Strong
          </div>
          <div class="filter-box__section-row">
            Less Strong
          </div>
        </div>
        <div class="filter-box__section">
          <div class="filter-box__section-header">
            <div class="filter-box__section-title">
              Review Icons
            </div>
            <div class="filter-box__section-header-icon">
              <img src="@/assets/images/add.svg" alt="add icon" />
            </div>
          </div>
          <div class="filter-box__section-row-icons">
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
          </div>
          <div class="filter-box__section-row-icons">
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star_outline.svg" alt="star outline icon" /></div>
          </div>
          <div class="filter-box__section-row-icons">
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star.svg" alt="star icon" /></div>
            <div><img src="@/assets/images/star_outline.svg" alt="star outline icon" /></div>
            <div><img src="@/assets/images/star_outline.svg" alt="star outline icon" /></div>
          </div>
        </div>
        <div class="filter-box__section">
          <div class="filter-box__section-header">
            <div class="filter-box__section-title">
              Tags
            </div>
          </div>
          <div class="filter-box__section-row">
            <div class="tag is-fullwidth">Test</div>
          </div>
          <div class="filter-box__section-row">
            <div class="tag is-fullwidth">Test</div>
          </div>
          <div class="filter-box__section-row">
            <div class="tag is-fullwidth">Test</div>
          </div>
        </div>
      </div>
    </div>
    <div class="page__main-content-area-with-panel">
      <!-- TYPOGRAPHY BOX STARTS HERE -->
      <div class="box">
        <div class="box__content">
          <h2>Page Layouts</h2>
          <!-- To simulate page layouts, we are creating a container and fixing the aspect ratio -->
          <!-- A macbook screen is 16x10, so we will use that. -->
          <h4>Page Layout 1 - Left Navbar</h4>
          <div class="laptop-screen">
            <div class="page">
              <div class="page__left-nav-bar">
                <div class="box">
                  <div class="box__content">
                    <span style="font-size: .75rem">
                      Navbar
                    </span>
                  </div>
                </div>
              </div>
              <div class="page__main-content-area">
                <div class="box">
                  <div class="box__header">
                    <div class="box__title">
                      <span style="font-size: .75rem">Main Content</span>
                    </div>
                  </div>
                  <div class="box__content">
                    <span style="font-size: .75rem"
                      >Lorem ipsum dolor sit, amet consectetur adipisicing elit. Ad non vero labore
                      aspernatur possimus quia, earum ducimus porro unde aut ab odio ipsa
                      consequatur laudantium iure, dolores quibusdam sed nemo?</span
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
          <h4>Page Layout 2 - Left Navbar / Right Info Panel</h4>
          <div class="laptop-screen">
            <div class="page">
              <div class="page__left-nav-bar">
                <div class="box">
                  <div class="box__content">
                    <span style="font-size: .75rem">
                      Navbar
                    </span>
                  </div>
                </div>
              </div>
              <div class="page__main-content-area-with-panel">
                <div class="box">
                  <div class="box__header">
                    <div class="box__title">
                      <span style="font-size: .75rem">Main Content</span>
                    </div>
                  </div>
                  <div class="box__content">
                    <span style="font-size: .75rem"
                      >Lorem ipsum dolor sit, amet consectetur adipisicing elit. Ad non vero labore
                      aspernatur possimus quia, earum ducimus porro unde aut ab odio ipsa
                      consequatur laudantium iure, dolores quibusdam sed nemo?</span
                    >
                  </div>
                </div>
              </div>
              <div class="page__right-panel">
                <div class="box">
                  <div class="box__content">
                    <span style="font-size: .75rem">
                      Right Info Panel
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="box">
        <div class="box__header">
          <span class="box__title">
            Typography
          </span>
        </div>
        <div class="box__content">
          <!-- HEADERS -->
          <h2>Headers</h2>
          <div>
            <h1>H1 Header</h1>
            <h2>H2 Header</h2>
            <h3>H3 Header</h3>
            <h4>H4 Header</h4>
            <h5>H5 Header</h5>
            <h6>H6 Header</h6>
          </div>
          <h4>Title / Subtitle</h4>
          <span class="is-title">Title</span>
          <span class="is-subtitle">Subtitle</span>

          <!-- CONTENT -->
          <h2>Content</h2>
          <div class="content">
            This is a regular paragraph of text. <strong>It has bold elements</strong> and
            <em>it has italicized elements</em>. Lorem ipsum dolor, sit amet consectetur adipisicing
            elit. Blanditiis architecto laborum quis at natus cumque beatae ut. Aperiam architecto
            nulla accusamus! Lorem ipsum dolor, sit amet consectetur adipisicing elit. Blanditiis
            architecto laborum quis at natus cumque beatae ut. Aperiam architecto nulla accusamus!
          </div>
          <!-- LISTS -->
          <h4>Unordered List</h4>
          <ul>
            <li>This is element one</li>
            <li>This is element two</li>
            <li>This is element three</li>
          </ul>
          <h4>Ordered List</h4>
          <ol>
            <li>This is element one</li>
            <li>This is element two</li>
            <li>This is element three</li>
          </ol>
        </div>
      </div>
      <!-- LAYOUT BOX STARTS HERE -->
      <div class="box">
        <div class="box__header">
          <span class="box__title">
            Layout
          </span>
        </div>
        <div class="box__content">
          <h2>Containers</h2>
          <h4>Generic Box</h4>
          <div class="box">
            <div class="box__header">
              <div class="box__title">
                Box Title
              </div>
            </div>
            <div class="box__content">
              <div class="content">
                <p>
                  This is some box content. Lorem ipsum, dolor sit amet consectetur adipisicing
                  elit. Molestiae facilis, ipsa excepturi obcaecati quidem provident eligendi
                  expedita labore officia consequuntur? Provident optio quos voluptas aliquid ut
                  nam, qui nesciunt atque!
                </p>
                <p>
                  This is some box content. Lorem ipsum, dolor sit amet consectetur adipisicing
                  elit. Molestiae facilis, ipsa excepturi obcaecati quidem provident eligendi
                  expedita labore officia consequuntur? Provident optio quos voluptas aliquid ut
                  nam, qui nesciunt atque!
                </p>
              </div>
            </div>
          </div>
          <h4>Box with Navbar</h4>
          <div class="box">
            <div class="box__tab-header">
              <div class="box__tab">
                Navbar 1
              </div>
              <div class="box__tab--active">
                Navbar 2
              </div>
              <div class="box__tab">
                Navbar 3
              </div>
            </div>
            <div class="box__content">
              <div class="row">
                <div class="action-callout">
                  Here's an example of a box with a callout, text and form inside of it.
                </div>
              </div>
              <div class="content">
                Lorem ipsum dolor sit amet, consectetur adipisicing elit. Laboriosam labore fugit
                laudantium maxime voluptatum veritatis atque dolor deleniti, repudiandae aut quo
                optio corporis, a ea quaerat dolores suscipit magnam libero?
              </div>
              <div class="flexbox-container">
                <div class="flexbox-container__column">
                  <div class="form">
                    <div class="form__element">
                      <div class="form__element-header">
                        Form Element 1
                      </div>
                      <input type="text" class="form__input" />
                    </div>
                  </div>
                </div>
                <div class="flexbox-container__column">
                  <div class="form">
                    <div class="form__element">
                      <div class="form__element-header">
                        Form Element 1
                      </div>
                      <input type="text" class="form__input" />
                    </div>
                  </div>
                </div>
              </div>
              <div class="flexbox-container">
                <div class="flexbox-container__column">
                  <div class="form__element">
                    <div class="form__element-header">
                      Text Area
                    </div>
                    <textarea type="text" rows="5" class="form__textarea" />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <h4>Item List</h4>
          <div class="item-list">
            <div class="item-list__header">
              <span class="item-list__title">
                This is an item list
              </span>
            </div>
            <div class="item-list__item">
              <div class="action-item">
                <div class="action-item__header">
                  <span class="title">This is the title</span>
                  <span class="action-item__title">
                    <img src="@/assets/images/add.svg" alt="add icon" />
                  </span>
                </div>
                <div class="action-item__content">
                  <div class="content">
                    Anythign can go in here. Maybe you want some spaced out content? Lorem, ipsum
                    dolor sit amet consectetur adipisicing elit. Perspiciatis ipsa officia
                    architecto incidunt dignissimos, nobis obcaecati impedit dolorem repellendus
                    delectus, sint blanditiis. Quae aliquid, distinctio in corporis quo officiis
                    numquam?
                  </div>
                </div>
              </div>
            </div>
            <div class="item-list__item">
              <div class="action-item">
                <div class="action-item__header">
                  <span class="title">This is the title</span>
                  <span class="action-item__title">
                    <img src="@/assets/images/add.svg" alt="add icon" />
                  </span>
                </div>
                <div class="action-item__content">
                  Or maybe you don't? Lorem ipsum dolor sit amet consectetur adipisicing elit.
                  Dignissimos modi itaque natus dolores fuga repudiandae laboriosam ratione ad
                  voluptatem nulla. Accusantium, voluptatibus quis provident in impedit labore quod
                  earum exercitationem.
                </div>
              </div>
            </div>
          </div>

          <h2>
            Full Width Action Callout (flexbox)
          </h2>
          <div class="action-callout">You are viewing a lead owned by:&nbsp<b>Mike Jones</b></div>
          <h2>
            Lead Lists
          </h2>
          <div class="lead-row lead-row--list">
            <div class="lead-row__title">
              <img src="@/assets/images/add.svg" alt="add icon" /> Lead List Name
            </div>
            <div class="lead-row__title">Number of Leads</div>
          </div>
          <div class="lead-row lead-row--list">
            <div class="lead-row__title">
              <img src="@/assets/images/add.svg" alt="add icon" /> Lead List Name
            </div>
            <div class="lead-row__title">Number of Leads</div>
          </div>
          <div class="lead-row lead-row--list">
            <div class="lead-row__title">
              <img src="@/assets/images/add.svg" alt="add icon" /> Lead List Name
            </div>
            <div class="lead-row__title">Number of Leads</div>
          </div>

          <div class="lead-row">
            <div class="lead-row__title">Lead Name</div>
            <div class="lead-row__item--double">Summary (double)</div>
            <div class="lead-row__item">$500</div>
            <div class="lead-row__item">3/4/20</div>
            <div class="lead-row__item"><button class="button">Button</button></div>
            <div class="lead-row__item"><button class="button">Button</button></div>
            <div class="lead-row__item--half">
              <img src="@/assets/images/add.svg" alt="add icon" />
            </div>
          </div>
          <div class="lead-row lead-row--gray">
            <div class="lead-row__title">Lead with tags</div>

            <div class="lead-row__item--double">
              <div class="tag">Tag 1</div>
              <div class="tag">Tag 2</div>
              <div class="tag">Tag 3</div>
            </div>
            <div class="lead-row__item">04/05/20</div>
            <div class="lead-row__item"><button class="button">Button</button></div>
            <div class="lead-row__item"><button class="button">Button</button></div>
            <div class="lead-row__item--half">
              <img src="@/assets/images/add.svg" alt="add icon" />
            </div>
          </div>
          <div class="lead-row lead-row--red">
            <div class="lead-row__title">Lead with Input Box</div>
            <div class="lead-row__item--double">Summary (double)</div>
            <div class="lead-row__item">$500</div>
            <div class="lead-row__item">3/4/20</div>
            <div class="lead-row__item--double"><input class="input" type="text" /></div>
          </div>
        </div>
      </div>
      <!-- FORM ELEMENTS BOX STARTS HERE -->
      <div class="box">
        <div class="box__header">
          <span class="box__title">
            Forms
          </span>
        </div>
        <div class="box__content">
          <!-- Form Element -->
          <h2>Forms</h2>
          <div class="form">
            <div class="form__header">
              This is some explantory information about the form. Lorem ipsum dolor sit amet
              consectetur adipisicing elit. Aut, quaerat quod. Numquam voluptas doloribus porro
              nihil repellat fuga itaque aliquid assumenda cum voluptatibus. Ipsa commodi nemo
              aliquid dolor, repellendus quam.
            </div>
            <div class="form__element">
              Every item in a form is wrapped in a form element to maintain spacing
            </div>
            <div class="form__element">
              <div class="form__element-header">Input</div>
              <div class="form__element-help">Help Text</div>
              <input type="text" class="form__input" />
              <div class="form__element-error">Error</div>
            </div>
            <div class="form__element">
              <div class="form__element-header">Text Area</div>
              <div class="form__element-help">Help Text</div>
              <textarea class="form__textarea" rows="8" />
              <div class="form__element-error">Error</div>
            </div>
            <div class="form__element">
              <div class="form__element-header">Select</div>
              <div class="form__element-help">Help Text</div>
              <select class="form__select">
                <option value="Test">Test</option>
                <option value="Test">Test</option>
                <option value="Test">Test</option>
                <option value="Test">Test</option>
              </select>
              <div class="form__element-error">Error</div>
            </div>
            <div class="form__element">
              <div class="form__element-header">Radio</div>
              <div class="form__element-help">Help Text</div>
              <div class="form__input-group">
                <input type="radio" id="element-1" name="radio-group" class="form__radio" />
                <label for="element-1">This is Element 1</label>
              </div>
              <div class="form__input-group">
                <input type="radio" id="element-2" name="radio-group" class="form__radio" />
                <label for="element-2">This is Element 2</label>
              </div>
              <div class="form__input-group">
                <input type="radio" id="element-3" name="radio-group" class="form__radio" />
                <label for="element-3">This is Element 3</label>
              </div>
              <div class="form__element-error">Error</div>
            </div>
            <div class="form__element">
              <div class="form__element-header">Checkboxes</div>
              <div class="form__element-help">Help Text</div>
              <div class="form__input-group">
                <input
                  type="checkbox"
                  id="checkbox-1"
                  name="checkbox-group"
                  class="form__checkbox"
                />
                <label for="checkbox-1">This is Element 1</label>
              </div>
              <div class="form__input-group">
                <input
                  type="checkbox"
                  id="checkbox-2"
                  name="checkbox-group"
                  class="form__checkbox"
                />
                <label for="checkbox-2">This is Element 2</label>
              </div>
              <div class="form__input-group">
                <input
                  type="checkbox"
                  id="checkbox-3"
                  name="checkbox-group"
                  class="form__checkbox"
                />
                <label for="checkbox-3">This is Element 3</label>
              </div>
              <div class="form__element-error">Error</div>
            </div>
          </div>
        </div>
      </div>
      <div class="box">
        <div class="box__header">
          <div class="box__title">Other Elements</div>
        </div>
        <div class="box__content">
          <h4>Buttons</h4>
          <button class="button">Here is a primary button</button>
          <button class="secondary-button">Here is a secondary button</button>
          <button class="inactive-button">Here is an inactive button</button>
          <h4>Tags</h4>
          <div class="tag">This is a tag</div>
          <div class="tag">They are inline</div>
          <div class="tag">It is cool</div>
        </div>
      </div>
    </div>
    <div class="page__right-panel">
      <div class="box">
        <div class="box__header">
          <div class="box__title">Test</div>
        </div>
        <div class="box__panel-row">
          <div class="box__panel-row-icon">
            <img src="@/assets/images/add.svg" alt="add icon" />
          </div>
          <div class="box__panel-row-content">
            <span class="is-title">Title</span>
            <span class="is-subtitle">Summary Text</span>
          </div>
        </div>
        <div class="box__panel-row">
          <div class="box__panel-row-icon">
            <img src="@/assets/images/add.svg" alt="add icon" />
          </div>
          <div class="box__panel-row-content">
            <span class="is-title">Title</span>
            <span class="is-subtitle">Summary Text</span>
          </div>
        </div>
        <div class="box__panel-row">
          <div class="box__panel-row-icon">
            <img src="@/assets/images/add.svg" alt="add icon" />
          </div>
          <div class="box__panel-row-content">
            <span class="is-title">Title</span>
            <span class="is-subtitle">Summary Text</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Styles',
  data() {
    return {}
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';

.laptop-screen {
  // This is a box that simulates the aspect ratio of a macbook. Useful for
  // showing "mini" versions of page layouts
  height: 450px;
  width: 720px;
  border: 1px solid black;
  margin: 2rem;
}
</style>
