#include <bur/plctypes.h>
#include <pp_gn.h>

#if 0
	typedef struct pid_typ
	{
		REAL	e;				/* control deviation e = w-x */
		REAL	Kp;				/* proportional gain */
		REAL	Ti;				/* integral action time */
		REAL	i_max;			/* maximum integral action */
		REAL	Td;				/* derivative action time */
		REAL	T1;				/* filter time */
		REAL	Ta;				/* sample time of PID controller */
		REAL	y_max;			/* output limitation */
		REAL	y;				/* output signal */
		REAL	yp;				/* proportional part */
		REAL	yi;				/* integral part */
		REAL	yd;				/* differencial part */
		REAL	ydt1;			/* filtered d-part by T1 */
		REAL	yp_old;			/* last yp used for d-part (internal use only) */
		REAL	i_lim;			/* actual anit wind-up limitation (internal use only) */
		USINT	yiHold;			/* 1 ...holds yi part at actual value */
	}	pid_typ;
#endif

#define pidMAX(a,b)	( (a) > (b)? (a):(b) ) 		/* find maximum */
#define pidMIN(a,b)	( (a) < (b)? (a):(b) ) 		/* find minimum */


/****************************************************************************
**********         				      pid()   				        *********
*****************************************************************************
*                                                                           *
*  Description:                                                             *
*     This function creates a PID controller according to the Smart Process *
*     Technology of ACOPOS                                                  *
*                                                                           *
*  Interface:                                                               *
*     Input:                                                                *
*       pPID      : pointer to PID info structure                  			*
*                                                                           *
*---------------------------------------------------------------------------*
*   History                                                                 *
*   Version     Date        Autor                                           *
*   01.00       02.08.03    W. Paulin     created 							*
****************************************************************************/
void pid(drcsPIDinf_typ *pPID)
{
	if (pPID == 0) return;
	
	pPID->yp = pPID->Kp * pPID->e;
																										/* P part */
	if (pPID->Ti > 0)	
	{
		pPID->i_lim  = pidMAX(pPID->i_max - abs(pPID->yp), 0);											/* I part with Anti-Windup */
		
		if (pPID->yiHold == 0)																			/* hold I part if requested */
		{
			pPID->yi = pidMAX(pidMIN(pPID->yi + pPID->yp*pPID->Ta/pPID->Ti, pPID->i_lim), -pPID->i_lim);
		}
	}
	else
	{
		pPID->yi = 0;
	}
	
	if (pPID->Ta > 0)	
	{
		pPID->yd     = pPID->Kp * pPID->Td/pPID->Ta * (pPID->yp-pPID->yp_old);							/* D part */
		pPID->yp_old = pPID->yp;

		if (pPID->T1 > 0)
		{
			pPID->ydt1 = (1-pPID->Ta/pPID->T1) * pPID->ydt1 + pPID->Ta/pPID->T1*pPID->yd;				/* DT1 part */
		}
		else
		{
			pPID->ydt1 = 0;
		}
	}
	else
	{
		pPID->yd     = 0;
		pPID->yp_old = 0;
		pPID->ydt1   = 0;
	}

	pPID->y = pPID->yp + pPID->yi + pPID->ydt1;															/* result value */	
	pPID->y = pidMAX(pidMIN(pPID->y, pPID->y_max), -pPID->y_max);										/* limit result value */
}

/* set initial values */
void pidInit(drcsPIDinf_typ *pPID)
{
	if (pPID == 0) return;
	
	pPID->y      = 0;
	pPID->yp     = 0;
	pPID->yi     = 0;
	pPID->yd     = 0;
	pPID->ydt1   = 0;
	pPID->yp_old = 0;
	pPID->i_lim  = 0;
}

