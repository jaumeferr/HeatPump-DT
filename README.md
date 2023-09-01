# Digital twinning your home heat pump system

![image](https://github.com/jaumeferr/HeatPump-DT/assets/36743497/5674ba72-5fc3-40b0-a387-ec12375540d6)

This work is focused on the world of Digital Twins, virtual and autonomous replicas of a real product, service or system that rely on information provided by its physical counterpart in order to reflect the current state of the system and to adapt predictively to the different episodes of its life cycle.

In this project, the benefits of digitizing domestic environments through the use of digital twins are studied. Specifically, the implemented solution is developed on the heat pump system deployed in the Innovation Center Ca Ses Llúcies in order to improve the efficiency and maintenance of the machine as well as the user's own comfort.
Before designing the digital twin application, a historical review of the background of digital twins is made, the main characteristics of the concept are presented and the state of the art is made known. Subsequently, the heat pump system that will be the case study of the project is presented and the needs to be covered by the designed digital twin are examined.

Based on a requirements analysis, a solution is designed using current technologies. The solution consists of an application based on the web development framework that allows real-time monitoring of the status of the heat pump in question, as well as simulating and predicting its future behavior using Machine Learning techniques. In this solution, two large blocks can be distinguished that will be communicated in real time and in constant dialogue:

The physical twin is in charge of collecting and communicating periodically the system's activity records by means of a physically installed sensor network. This connection between physical and digital twin is made through an intermediary server, which allows to establish a real-time and bidirectional communication.

The digital twin stores the data collected by the physical twin in a module dedicated to managing large amounts of data. On the one hand, this information can be directly processed in real time in order to analyze the current state of the system. This operation is performed by a system of events and alerts based on the static rules that define the operation of a heat pump system. On the other hand, the accumulated historical data together combined witg meteorological information provided by external sources is used as a input for predictive models based on Machine Learning. These models make it possible to simulate the behavior of the real system in future scenarios. In addition, the digital twin offers the user a convenient and intuitive tool for monitoring and interacting with the machine through the browser.

Once the digital twin has been designed and implemented, a series of tests are carried out to demonstrate the usefulness of the developed system and to verify that the model is fully functional and meets the main expectations of the twins.

Although the proof of concept shows that these points are covered, a series of future works aimed at further highlighting the usefulness of digital twins are presented. The paper ends with the conclusions, which show that the objectives have been met.

The full document can be accessed from here: https://github.com/jaumeferr/HeatPump-DT/tree/main/DT-Teoria (spanish originaL) OR *coming soon* (english version)
